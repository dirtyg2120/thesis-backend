{ pkgs, inputs, ... }:
let
  pythonEnv = inputs.mach-nix.lib.${pkgs.system}.mkPython {
    requirements = builtins.readFile ./requirements.txt + ''
      python-lsp-server[mccabe,pyflakes,rope]
      pylsp-mypy
      python-lsp-black
      pyls-isort>=0.2.2
      flake8
      flake8-isort
      flake8-black
    '';
  };
in
{
  devshell.packages = [ pythonEnv ];
  env = [
    {
      name = "MYPY_CACHE_DIR";
      eval = "$PRJ_DATA_DIR/mypy_cache";
    }
    {
      name = "PYTEST_ADDOPTS";
      eval = ''--override-ini=cache_dir=\"$PRJ_DATA_DIR\"/pytest_cache'';
    }
  ];
  commands = [{
    name = "up";
    command = ''
      ${pkgs.podman}/bin/podman run -d --rm --publish 27017:27017 \
        -v "$PRJ_DATA_DIR"/mongodb:/data/db mongo:4.0
    '';
    help = "Start MongoDB";
  }];
}
