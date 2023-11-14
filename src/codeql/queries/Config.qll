import python

module Config {
  predicate constrainLocation(Location loc) { loc.getFile().getAbsolutePath().matches("%/test.py") }
}
