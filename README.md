# ClipSaver

This workflow is triggered with the `cs` keyword by default.

It presents images from Alfred's clipboard history via a Script Filter, and allows selecting an image to be extracted, converted to a format of your choice (default is PNG) and placed in a folder of your choosing (default is on the Desktop, in a folder called `saved_clips`). You can optionally set the `save_to_current` environment variable to have the workflow save to the currently active Finder window.

Upon success, the original clipboard entry as well as the .tiff from Alfred's database will be removed if you have `delete_after_convert` set to true (File List objects in the clipboard history will remain untouched).

## Workflow Configuration

All configuration is optional. The workflow should work "out of the box" without configuring any of these items. They are here for advanced users only.

- `db_name` - override to specify a custom clipboard database file if needed
- `db_path` - override the default clipboard database path
- `dest_dir` where to save images if `save_to_current == false`, defaults to `~/Desktop/saved_clips`
- `sf_clip_limit` (default: empty) an optional limit to constrain the number of results displayed in the Script Filter
- `save_to_current` (default: false) - set to `true` if you want the workflow to put saved images in the directory of the "frontmost" Finder window
- `default_format` (default: png) - set to e.g. `jpg` etc. You can override per invocation by passing as an argument (use `sips --formats` to see all available formats)
- `delete_after_convert` (default: false) - set to `true` if you want the source images deleted after successful conversion

## Usage Tips

- Tap `⇧SHIFT` while navigating through Script Filter results to get a QuickLook preview of the image. While QL is displayed, you can use the Arrow keys to flip through results.
- Tap `⌥OPTION` to show the path to the app that created that image in the subtitle
- Hold `⌘CMD` when actioning the item to Reveal the original image in Alfred's db folder
- Pass a number as an argument to the script to save X number of clips in bulk
- Pass an image format e.g. `jpeg` as an argument to override your default format

## Screenshot:
<img width=500 src=https://raw.githubusercontent.com/luckman212/alfred_clipsaver_workflow/main/clipsaver.png>

## Download:
https://github.com/luckman212/alfred_clipsaver_workflow/releases/latest/

## Forum topic:
https://www.alfredforum.com/topic/14400-clipsaver-save-images-from-clipboard-history-to-png-files/
