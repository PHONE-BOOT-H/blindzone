import Link from "next/link";

export default function Nav() {
  return (
    <nav className="border-b bg-white">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold">BlindZone</Link>
        <div className="flex gap-6 text-sm">
          <Link href="/" className="hover:underline">시민 모드</Link>
          <Link href="/policy" className="hover:underline">정책 시뮬레이터</Link>
          <Link href="/about" className="hover:underline">About</Link>
        </div>
      </div>
    </nav>
  );
}
