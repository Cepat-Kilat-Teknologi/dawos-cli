# Homebrew Formula for dawos-cli
#
# To use this formula, create a tap repository:
#   1. Create repo: github.com/Cepat-Kilat-Teknologi/homebrew-tap
#   2. Copy this file to Formula/dawos-cli.rb in that repo
#   3. Update the url and sha256 for each release
#
# Users can then install with:
#   brew tap Cepat-Kilat-Teknologi/tap
#   brew install dawos-cli

class DawosCli < Formula
  include Language::Python::Virtualenv

  desc "Remote CLI client for dawos-agent — manage PPPoE/BNG routers"
  homepage "https://github.com/Cepat-Kilat-Teknologi/dawos-cli"
  # TODO: Update URL and sha256 for each release
  url "https://github.com/Cepat-Kilat-Teknologi/dawos-cli/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  head "https://github.com/Cepat-Kilat-Teknologi/dawos-cli.git", branch: "main"

  depends_on "python@3.12"

  resource "typer" do
    url "https://files.pythonhosted.org/packages/typer/typer-0.9.0.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/httpx/httpx-0.27.0.tar.gz"
    sha256 "PLACEHOLDER"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/rich/rich-13.7.0.tar.gz"
    sha256 "PLACEHOLDER"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "dawos-cli", shell_output("#{bin}/dawos --version")
  end
end
