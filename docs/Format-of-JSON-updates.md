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

Except for Separator Items, each Menu Item has a `title` string field for the actual item text and an `active` boolean flag field which usually renders as a checkmark if set to `true`.

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

Such a Menu Item can not be clicked and is usually shown as greyed-out. This can also be used to convey for some extra information beyond the status bar.


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

After the optional user text prompt, this sends the configured HTTP request with any prompt placeholders replaced by the actual user input.


##### GUI Prompt

TBD.



##### HTTP Request

TBD.


