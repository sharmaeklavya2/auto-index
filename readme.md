# Auto-Index

Recursively generate a directory listing for every directory.

### Live example

[My downloads website](https://sharmaeklavya2.github.io/dl/)

### How to run

    ./index.py <dirpath>

### Features

* Looks better than apache and nginx default server index pages.
* No static assets required on deployment
(but you can optionally use the `--external-style` flag to put
`index-style.css` at the root to take advantage of caching).
* Lightweight: no JavaScript required; CSS less than 0.5 KB.
* SVG icons: included as
[data URLs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs);
only required icons are loaded.

### Excluding

* To exclude an automatic index from being created in a directory,
place a `.noindex` file in that directory.
* To exclude a directory from being visible in an index,
set its read permission for others (`S_IROTH`) to false.

### Credits

SVG icons are derived from [FontAwesome](https://github.com/FortAwesome/Font-Awesome).
I modified their dimensions and color.

### License

Everything except the icons is licensed under the MIT License (see `LICENSE.txt`).
