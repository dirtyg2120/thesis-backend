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
    nixpkgs.lib.flake.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShell = (pkgs.devshell.eval {
          configuration = ./devshell.nix;
          extraSpecialArgs = { inherit inputs; };
        }).shell;
      });
}
