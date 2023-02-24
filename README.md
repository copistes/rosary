# Rosary

Rosary is a python-based implementation for the console. It can help you recitate the rosary by unfolding the daily rosary according to the liturgical momement.


## Installation

```
git clone https://github.com/copistes/rosary.git
cd rosary
pip install .
```

## Usage

Run rosary by calling `rr`, it will display the current step in your rosary. Type enter to continue. At any moment interrup with `CTRL+C` and when you resume you will be at the same step.

Example output:

```
Friday of Lent studying Sorrowful Mysteries
✝ Credo
① Hail Mary
② Hail Mary
③ Hail Mary
⓿ Glory to the Father
⓿ Our Father
⓿ The Agony of Jesus in the Garden of Gethsemane
...
```

## ChatGPT Support

Rosary stores its state in the `~/.rosary` file. If you add an [openAI key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) you can use chatGPT to generate sermons for each mystery.

To do so add your key in the `~/.rosary` file such as:

```json
{
    "openai": "XXXX",
}
```

It will then generate texts for the mysteries:

```
⓿ The Agony of Jesus in the Garden of Gethsemane

The Agony of Jesus in the Garden of Gethsemane is a powerful reminder of the
immense suffering Jesus endured for us. He was so overwhelmed with sorrow and
anguish that he sweat drops of blood. He asked his disciples to stay and pray
with him, but they fell asleep. Jesus was willing to accept the will of God and
his ultimate sacrifice for us. He showed us that even in the darkest of times,
we can trust in God's love and mercy.
```


## Help

```
usage: rr [-h] [-r] [-n] [-s] [-p]

Rosary an app to pray during the programmer's day.

optional arguments:
  -h, --help      show this help message and exit
  -r, --reset     Reset current rosary
  -n, --nosermon  Disable CHAT GPT sermon
  -s, --single    Only do a single step
  -p, --print     Only print current rosary and liturgical time
```


## Licences

This is LGPL.