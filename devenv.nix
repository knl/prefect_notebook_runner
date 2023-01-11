{ pkgs, ... }:

{
  # https://devenv.sh/basics/

  # https://devenv.sh/packages/

  # https://devenv.sh/languages/
  languages = {
    python.enable = true;
    python.package = pkgs.python37;
  };

  # https://devenv.sh/scripts/
  # scripts.hello.exec = "echo hello from $GREET";

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.black.enable = true;
  # pre-commit.hooks.isort.enable = true;
  # pre-commit.hooks.flake8.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";
}
