# Format of JSON updates

## Update

An update for the AllBar app is a JSON object with 3 required fields:

- `ttl` [Time To Live](#time-to-live)
- `indicators` [Status Bar Indicators](#status-bar-indicators)
- `menu` [Menu Items](#menu-items)

Here is a quick example:

```json
{
  "ttl": 0,
  "indicators": [
    "1:05",
    "1 05"
  ],
  "menu": [
    {
      "title": "Click me!",
      "active": false,
      "open": "https://www.google.com"
    }
  ]
}
```


### Time To Live

The `ttl` field is an integer. It measures the duration in seconds for which the update data is valid. It can be 0 or a positive integer.


### Status Bar Indicators

The `indicators` field is an array. It lists multiple indicators which are shown in the status bar for about 1 second each and then looped back from the beginning. This allows for slow animations like a blinking ":" in a timer display. If you don't want any animation, you can just put 1 indicator into the list.

The `indicators` array elements all have to be of the same type and can be one of the following:

- [Text Only Status Bar Indicators](#text-only-status-bar-indicators)
- [Icon Status Bar Indicators (with optional text)](#icon-status-bar-indicators-with-optional-text)


#### Text Only Status Bar Indicators

Each indicator is just a simple string. Keep it short, real estate on the status bar is expensive.

Consider using Unicode symbols as easy replacements for Icon Status Bar Indicators. That saves you the hassle of having to create the icon PNG files.


#### Icon Status Bar Indicators (with optional text)

Each indicator is an object with an `icon` field and an optional `title` field.

The `icon` field is a string and must contain a [data: URL](https://en.wikipedia.org/wiki/Data_URI_scheme) of a PNG image. The PNG image should be maximal 20 pixels high and can be as wide as you have room in your status bar. ;-)

Other solutions only allow for a pre-determined set of icons to pick from, but with AllBar the "icon" itself is delivered together with each update. This allows for "dynamic" graphics like miniature diagrams of real-time values and similar things.

The optional `title` field is a string. It saves you from writing text into the "icon" image file. Again, keep the text short, real estate on the status bar is expensive.


### Menu Items

The `menu` field is an array. Each array element is a JSON object and can be one of the following:

- [Menu Separator Item](#menu-separator-item)
- [Disabled Menu Item](#disabled-menu-item)
- [Menu Item to open URL](#menu-item-to-open-url)
- [Menu Item to send an HTTP request](#menu-item-to-send-an-http-request)

Each Menu Item (except for Separator Items) has:

- a `title` string field for the actual item text
- an `active` boolean flag field which usually renders as a checkmark if set to `true`

Sub-menus with nested items are not supported yet.


#### Menu Separator Item

This is a JSON object with a single boolean field `separator` which must be set to `true`:

```json
{"separator": true}
```


#### Disabled Menu Item

This is a JSON object with `title` and `active` fields and a boolean field `disabled` which must be set to `true`:

```json
{
  "title": "Grey Extra Info",
  "active": false,
  "disabled": true
}
```

Such a Menu Item can not be clicked and is usually shown as greyed-out. This can also be used to reveal some extra information when the status bar indicator gets clicked.


#### Menu Item to open URL

This is a JSON object with `title` and `active` fields and a string field `open` which must contain a valid fully qualified URL:

```json
{
  "title": "Click me!",
  "active": false,
  "open": "https://www.google.com"
}
```

Clicking this Menu Item opens the configured URL in the default web browser. Use this for advanced actions beyond just clicking a menu item in the status bar menu.


#### Menu Item to send an HTTP request

This is a JSON object with the usual `title` and `active` fields, and:

- [an optional `prompt` field](#gui-prompt)
- [a `request` field](#http-request)

Here is a quick example:

```json
{
  "title": "Search something?",
  "active": false,
  "prompt": {
    "title": "Search the Internet",
    "message": "Please input some search text:",
    "placeholder": "prompt_placeholder"
  },
  "request": {
    "method": "GET",
    "url": "https://www.google.com/search?q=prompt_placeholder"
  }
}
```

If the `prompt` field is present, a GUI dialog with a single text field will be shown after clicking the Menu Item.

Currently, there is no validation of the user input, so it can even turn out to be an empty string.

Once that dialog is confirmed by clicking the "OK" button, the configuration of the HTTP request will be scanned for occurrences of the prompt placeholder string, which will then be replaced by the actual user input.

Then the HTTP request will be sent of as configured.

If the `prompt` field is not present, then the HTTP request will be sent off as configured right away.

Currently, any HTTP response is disregarded. I could imagine that in a future version it could get parsed and a notification bubble could be shown as a feedback of success or failure.


##### GUI Prompt

The `prompt` field is a JSON object with three fields:

- `title` a string to be shown as the window title of the GUI dialog
- `message` a string to be shown as the introductory text of the GUI dialog
- `placeholder` a string which will be searched for in the configuration of the HTTP request, to be replaced by the actual user input at the GUI dialog. Replacements in the URL and in header values will be URL-encoded, replacements in field values of the request body will be verbatim, since the body will get encoded anyways, as specified in the `Content-Type` header.

Here is a quick example:

```json
{
  "title": "Search the Internet",
  "message": "Please input some search text:",
  "placeholder": "prompt_placeholder"
}
```


##### HTTP Request

The `request` field is a JSON object with four fields:

- `method` a string to be used as the HTTP request method. See also https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
- `url` a string containing the fully qualified URL to send the HTTP request to.
- `headers` a JSON object with only strings as property values. Property names are HTTP request header names, and property values are header values. The `Content-Type` header is restricted to either `application/json` or `application/x-www-form-urlencoded`, the only two ways the AllBar app knows how to encode a request body. See also https://en.wikipedia.org/wiki/List_of_HTTP_header_fields#Request_fields
- `body` a JSON object. It can have nested values for `application/json` and should be flat for `application/x-www-form-urlencoded`.

Here is a quick example:

```json
{
  "method": "GET",
  "url": "https://www.google.com/search?q=prompt_placeholder",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Token 0123456789abcdef0123456789abcdef",
    "X-Prompted": "The answer is prompt_placeholder."
  },
  "body": {
    "field1": "value1",
    "field2": {
      "field2.1": "value2.1",
      "field2.2": "value2.2",
      "field2.3": "value2.3 is prompt_placeholder",
    },
    "field3": "value3"
  }
}
```
