class Timeout < Formula
  desc "Standalone GNU timeout, without installing the rest of coreutils"
  homepage "https://github.com/KSonny4/timeout"
  url "https://ftp.gnu.org/gnu/coreutils/coreutils-9.12.tar.xz"
  mirror "https://ftpmirror.gnu.org/coreutils/coreutils-9.12.tar.xz"
  sha256 "a480198559733e9b3da999e90543ac6f888a2caa544d8d664c5a1f17e528e210"
  license "GPL-3.0-or-later"

  conflicts_with "coreutils", because: "both install the timeout command; keep coreutils if already installed"

  def install
    system "./configure", "--disable-nls", "--disable-dependency-tracking",
           "--without-libgmp", "--without-selinux", *std_configure_args
    (buildpath/"standalone.mk").write <<~MAKE
      .PHONY: standalone-built-sources
      standalone-built-sources: $(BUILT_SOURCES)
    MAKE
    system "make", "-f", "Makefile", "-f", "standalone.mk", "standalone-built-sources"
    system "make", "src/timeout"
    bin.install "src/timeout"
    doc.install "COPYING", "AUTHORS"
  end

  test do
    assert_match "timeout (GNU coreutils) 9.12", shell_output("#{bin}/timeout --version")
    assert_equal "ok\n", shell_output("#{bin}/timeout 2 sh -c 'printf \"ok\\n\"'")
    shell_output("#{bin}/timeout .1 sleep 10", 124)
    shell_output("#{bin}/timeout --preserve-status .1 sleep 10", 143)
    shell_output("#{bin}/timeout --foreground -s0 -k.1 .1 sleep 10", 137)
  end
end
