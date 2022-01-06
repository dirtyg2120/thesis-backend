{ pkgs, inputs, ... }:
let
  pythonEnv = inputs.mach-nix.lib.${pkgs.system}.mkPython {
    requirements = builtins.readFile ./requirements.txt + ''
      python-lsp-server[mccabe,pyflakes,rope]
      pylsp-mypy
      python-lsp-black
      pyls-isort>=0.2.2
    '';
  };
in
{
  devshell.packages = [ pythonEnv ];
  env = [{ name = "MYPY_CACHE_DIR"; eval = "$PRJ_DATA_DIR/mypy_cache"; }];
}
