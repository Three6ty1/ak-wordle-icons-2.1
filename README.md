# Arknights Wordle Icons and Database repo

Will automatically pull from the Arknights EN (Global) Datamine repo which this is forked from and update the `operator_db.json` and icons for [Arknights Wordle](https://ak-wordle.three6ty1.dev/)

Thank you to NikitaZero from the Arknights wiki.gg team for pointing me in the right direction.

Thanks to g-otn for giving me the external push to update the repo/game

## Scripts
This is in run order:

#### `sync.yml`
- From the `master` branch. Triggers periodically
- Pulls down database information and runs the build script
#### `update.yml`
- From this `en` branch. Will trigger when a `.png` is updated in the gamedata folder which is where the information for characters are stored
#### `clean.py`
- Remove unnecessary png files that are not operators from the `charavatars` directories
#### `build.py`
- Build the operator database json
#### `convert.sh`
- Convert remaining pngs from `clean` step to webps to compress file size down (sometimes by over 10x)
#### `sanity_check.py`
- Check that all database entries have a corresponding icon
- Check that all icons are in the correct directory so that they can be referenced by the app
- The update will fail otherwise
- Note: This may need to be tweaked as the source of the game data json and the source for icons are not the same repo, therefore they may update desynced
#### `seed.ts`
- Add new operators to the database and be accessed by the game.

## Manually sanity check
#### Check race information
Can double check race with [handbook_team_table.json](https://github.com/Kengxxiao/ArknightsGameData_YoStar/blob/main/en_US/gamedata/excel/handbook_team_table.json)

#### Check operator list and count
Wiki.gg site https://arknights.wiki.gg/wiki/Operator/List
