import { useRef, useEffect } from 'react';

export default function Waveform() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rafRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d')!;
    const dpr = Math.min(window.devicePixelRatio, 2);

    function resize() {
      const w = canvas!.clientWidth;
      const h = canvas!.clientHeight;
      canvas!.width = w * dpr;
      canvas!.height = h * dpr;
      ctx!.scale(dpr, dpr);
    }
    resize();

    let t = 0;
    function draw() {
      const w = canvas!.clientWidth;
      const h = canvas!.clientHeight;
      ctx!.clearRect(0, 0, w, h);

      ctx!.strokeStyle = 'rgba(225, 247, 57, 0.6)';
      ctx!.lineWidth = 1;
      ctx!.beginPath();

      for (let x = 0; x < w; x++) {
        const normalizedX = x / w;
        const y =
          h / 2 +
          Math.sin(normalizedX * 8 + t) * 6 *
            Math.sin(normalizedX * 3 + t * 0.7) *
            Math.cos(normalizedX * 5 - t * 0.3);
        if (x === 0) {
          ctx!.moveTo(x, y);
        } else {
          ctx!.lineTo(x, y);
        }
      }
      ctx!.stroke();

      t += 0.03;
      rafRef.current = requestAnimationFrame(draw);
    }
    rafRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(rafRef.current);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: '100%',
        height: '40px',
      }}
    />
  );
}
