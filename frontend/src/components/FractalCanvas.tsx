import { useRef, useEffect } from 'react';

const VERTEX_SHADER = `
attribute vec2 a_pos;
void main() {
  gl_Position = vec4(a_pos, 0.0, 1.0);
}
`;

const FRAGMENT_SHADER = `
precision highp float;

const float PI = 3.14159265359;

uniform vec2 u_res;
uniform float u_time;
uniform float u_spike;
uniform float u_scene;
uniform vec2 u_rotateSpeed;

mat3 rotX(float a) {
  return mat3(
    1.0, 0.0, 0.0,
    0.0, cos(a), -sin(a),
    0.0, sin(a), cos(a)
  );
}

mat3 rotY(float a) {
  return mat3(
    cos(a), 0.0, sin(a),
    0.0, 1.0, 0.0,
    -sin(a), 0.0, cos(a)
  );
}

mat3 rotZ(float a) {
  return mat3(
    cos(a), -sin(a), 0.0,
    sin(a), cos(a), 0.0,
    0.0, 0.0, 1.0
  );
}

vec3 polarFold(vec3 p, float n) {
  float angle = atan(p.y, p.x);
  float r = length(p.xy);
  float sector = PI / n;
  angle = mod(angle + sector, 2.0 * sector) - sector;
  return vec3(cos(angle) * r, sin(angle) * r, p.z);
}

float sdTriPrismXY(vec3 p, vec2 h) {
  vec2 q = abs(p.xy);
  return max(
    max(q.x - h.y, max(q.x * 0.866025 + q.y * 0.5, q.y) * 2.0 - h.x),
    abs(p.z) - h.x
  );
}

float map(vec3 p) {
  float s = mix(1.5, 2.5, u_scene);
  float sp = mix(0.8, 1.5, u_spike);

  p = polarFold(p, 6.0);
  p.x -= s;
  p /= sp;

  float d1 = sdTriPrismXY(p, vec2(0.6 * sp, 0.06 * sp)) / sp;
  float d2 = abs(length(p) - 0.2 * sp) / sp;

  return min(d1, d2);
}

vec3 calcNormal(vec3 p) {
  vec2 e = vec2(0.001, 0.0);
  vec3 n = map(p) - vec3(
    map(p - e.xyy),
    map(p - e.yxy),
    map(p - e.yyx)
  );
  return normalize(n);
}

void main() {
  vec2 uv = (gl_FragCoord.xy - 0.5 * u_res.xy) / u_res.y;

  vec3 ro = vec3(0.0, 0.0, -3.5);
  vec3 rd = normalize(vec3(uv, 1.0));

  float t = u_time * 0.2;

  ro *= rotY(t * u_rotateSpeed.x);
  rd *= rotY(t * u_rotateSpeed.x);
  ro *= rotX(t * u_rotateSpeed.y);
  rd *= rotX(t * u_rotateSpeed.y);

  float d0 = 0.0;
  for (int i = 0; i < 64; i++) {
    vec3 p = ro + rd * d0;
    float dS = map(p);
    d0 += dS;
    if (dS < 0.001 || d0 > 20.0) break;
  }

  vec3 p = ro + rd * d0;
  vec3 n = calcNormal(p);

  vec3 col = vec3(0.4, 0.42, 0.45);
  float diff = max(0.0, dot(n, normalize(vec3(1.0, 2.0, 3.0))));
  col *= 0.8 + 0.2 * diff;

  float fresnel = pow(1.0 - max(0.0, dot(n, -rd)), 3.0);
  col += vec3(0.1, 0.1, 0.12) * fresnel;

  float fog = exp(-0.05 * d0 * d0);
  col = mix(vec3(0.05, 0.05, 0.06), col, fog);

  gl_FragColor = vec4(col, 1.0);
}
`;

export default function FractalCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);
  const stateRef = useRef({
    velX: 0,
    velY: 0,
    rotX: 0,
    rotY: 0,
    spikeTarget: 0.5,
    spikeCurrent: 0.5,
    autoScene: 0.5,
    prefersReduced: false,
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const state = stateRef.current;
    state.prefersReduced = prefersReduced;
    state.autoScene = prefersReduced ? 0.5 : 0;

    const gl = canvas.getContext('webgl', { antialias: false, alpha: false });
    if (!gl) return;

    // Compile shaders
    function createShader(gl: WebGLRenderingContext, type: number, source: string) {
      const shader = gl.createShader(type)!;
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      return shader;
    }

    const vs = createShader(gl, gl.VERTEX_SHADER, VERTEX_SHADER);
    const fs = createShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);

    const program = gl.createProgram()!;
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    gl.useProgram(program);

    // Fullscreen triangle
    const vertices = new Float32Array([-1, -1, 3, -1, -1, 3]);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const aPos = gl.getAttribLocation(program, 'a_pos');
    gl.enableVertexAttribArray(aPos);
    gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

    // Uniforms
    const uRes = gl.getUniformLocation(program, 'u_res');
    const uTime = gl.getUniformLocation(program, 'u_time');
    const uSpike = gl.getUniformLocation(program, 'u_spike');
    const uScene = gl.getUniformLocation(program, 'u_scene');
    const uRotate = gl.getUniformLocation(program, 'u_rotateSpeed');

    // Resize
    function resize() {
      const dpr = Math.min(window.devicePixelRatio, 1.5);
      const w = canvas!.clientWidth;
      const h = canvas!.clientHeight;
      canvas!.width = w * dpr;
      canvas!.height = h * dpr;
      gl!.viewport(0, 0, canvas!.width, canvas!.height);
    }
    resize();
    window.addEventListener('resize', resize);

    // Render loop
    function render(now: number) {
      if (!state.prefersReduced) {
        state.autoScene = 0.5 + 0.5 * Math.sin(now * 0.0001);
      }

      state.spikeCurrent += (state.spikeTarget - state.spikeCurrent) * 0.02;

      state.velX *= 0.95;
      state.velY *= 0.95;
      state.rotX += state.velX;
      state.rotY += state.velY + 0.001;

      gl!.uniform2f(uRotate, state.rotX, state.rotY);
      gl!.uniform1f(uSpike, state.spikeCurrent);
      gl!.uniform1f(uScene, state.autoScene);
      gl!.uniform2f(uRes, canvas!.width, canvas!.height);
      gl!.uniform1f(uTime, now * 0.001);
      gl!.drawArrays(gl!.TRIANGLES, 0, 3);

      rafRef.current = requestAnimationFrame(render);
    }
    rafRef.current = requestAnimationFrame(render);

    // Mouse interaction
    function onMouseMove(e: MouseEvent) {
      const rect = canvas!.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      state.velX += (x / rect.width - 0.5) * 0.005;
      state.velY += (y / rect.height - 0.5) * 0.005;
    }
    canvas.addEventListener('mousemove', onMouseMove);

    return () => {
      cancelAnimationFrame(rafRef.current);
      window.removeEventListener('resize', resize);
      canvas.removeEventListener('mousemove', onMouseMove);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        zIndex: 0,
      }}
    />
  );
}
