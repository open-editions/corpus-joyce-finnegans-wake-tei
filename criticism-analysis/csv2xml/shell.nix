{ nixpkgs ? import <nixpkgs> {} }:
let
  inherit (nixpkgs) pkgs;
  ghc = pkgs.haskellPackages.ghcWithPackages (ps: with ps; [
          vector xml-conduit cassava haskell-language-server
        ]);
in
pkgs.stdenv.mkDerivation {
  name = "my-haskell-env-4";
  buildInputs = [ ghc ];
  shellHook = ''
    export NIX_GHC="$(which ghc)"
    export NIX_GHCPKG="$(which ghc-pkg)"
    export NIX_GHC_DOCDIR="$NIX_GHC/../../share/doc/ghc/html"
    export NIX_GHC_LIBDIR="$(ghc --print-libdir)"
    eval $(egrep ^export ${ghc}/bin/ghc)
  '';
}
