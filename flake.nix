{
  inputs = {
    nixpkgs.url = "local";

    mach-nix.url = "github:DavHau/mach-nix";
    mach-nix.inputs.pypi-deps-db.follows = "pypi-deps-db";
    mach-nix.inputs.nixpkgs.follows = "nixpkgs";

    pypi-deps-db.url = "github:DavHau/pypi-deps-db";
    pypi-deps-db.flake = false;
  };

  outputs = { self, nixpkgs, ... }@inputs:
    nixpkgs.lib.flake.eachSystem [ "x86_64-linux" ] (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = (pkgs.devshell.eval {
          configuration = ./devshell.nix;
          extraSpecialArgs = { inherit inputs; };
        }).shell;
        checks =
          let
            pythonEnv = inputs.mach-nix.lib.${system}.mkPython {
              requirements = builtins.readFile ./requirements.txt + ''
                setuptools
                flake8
                flake8-isort
                flake8-black
                mypy
              '';
            };
          in
          {
            lint = pkgs.runCommandLocal "lint"
              {
                src = ./.;
                nativeBuildInputs = [ pythonEnv ];
              } ''
              cd $src
              flake8 --show-source --statistics --count
              touch $out
            '';
            test = pkgs.runCommandLocal "test"
              {
                src = ./.;
                nativeBuildInputs = [ pythonEnv ];
              } ''
              cd $src
              pytest -p no:cacheprovider app/tests
              touch $out
            '';
            type-check = pkgs.runCommandLocal "type-check"
              {
                src = ./.;
                nativeBuildInputs = [ pythonEnv ];
              } ''
              cd $src
              mypy --no-incremental --package=app
              touch $out
            '';
          };
      });
}
