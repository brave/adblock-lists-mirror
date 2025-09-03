This repo serves as a mirror for adblock lists that are shipped to Brave browser clients. The downloaded and validated lists are committed into https://github.com/brave-experiments/adblock-lists-mirror/commits/lists/lists. 

See: https://github.com/brave/brave-core-crx-packager/issues/884

### Searching lists in this repo

The filter lists are not stored in the default branch of this repository, so GitHub will not index their content for searching.
If you want to search for filters in the lists, it's recommended to do so on your local device.
The following commands may be useful:

```sh
# Quickly clone the latest list versions (without history)
git clone -b lists --depth 1 git@github.com:brave/adblock-lists-mirror.git
# Quickly clone a specific commit (without history)
git clone --revision=<full-commit-hash> --depth 1 git@github.com:brave/adblock-lists-mirror.git
```
