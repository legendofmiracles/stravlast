{ pkgs, ... }:

{
  # https://devenv.sh/packages/
  packages = [ pkgs.git ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    venv = {
      enable = true;
      requirements = ''
        stravalib
        ipdb
      '';
    };
  };

  pre-commit.hooks.black.enable = true;
}
