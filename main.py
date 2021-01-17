import discord
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import statistics
from token import token


client = discord.Client()

scores = []


def save():
    if loaded:
        toSave = {}
        for i in scores:
            toSave[i.name] = (i.points, i.serverid, i.max)
        out_file = open("scores.json", "w")
        json.dump(toSave, out_file, indent=6)
        out_file.close()





class score:
    def __init__(self, name, serverid):
        self.points = []
        self.name = name
        self.serverid = serverid
        self.max = 20

    def add_point(self, point):
        if 0 <= point <= self.max:
            self.points.append(point)

    def rm_point(self, point):
        self.points.remove(point)

    async def render(self, channel, plottype="normal"):
        coords = []
        for i in [int(k+0.5) for k in self.points]:
            for j in coords:
                if j[0] == i:
                    j[1] += 1
                    break
            else:
                coords.append([i, 1])

        for i in range(max(max([j[0] for j in coords]), self.max) + 1):
            if i not in [j[0] for j in coords]:
                coords.append([i, 0])

        coords.sort(key=lambda tup: tup[0])

        print(coords)
        message = 'Graph of scores rounded to integer of {}'.format(self.name)
        if plottype == "normal":
            plt.xticks([i[0] for i in coords])
            plt.yticks([i[1] for i in coords])
            plt.plot([i[0] for i in coords], [i[1] for i in coords], '#7289DA',  marker='o')
            plt.xlabel('score')
            plt.ylabel('aantal')
            plt.ylim(bottom=0)
            plt.xlim(left=0)
        elif plottype == "bar":
            message = 'Bargraph of scores rounded to integer of {}'.format(self.name)
            plt.xticks([i[0] for i in coords])
            plt.yticks([i[1] for i in coords])
            plt.bar([i[0] for i in coords], [i[1] for i in coords], color='#7289DA')
            plt.xlabel('score')
            plt.ylabel('aantal')
        elif plottype == 'pie':
            message = 'Piegraph of scores rounded to integer of {}'.format(self.name)
            explode = []
            maxcoord = max([i[1] for i in coords if i[1] != 0])
            for i in coords:
                if i[1] != 0 and i[1] == maxcoord:
                    explode.append(0.1)
                elif i[1] != 0:
                    explode.append(0)

            plt.pie([i[1] for i in coords if i[1] != 0], labels=[str(i[0]) for i in coords if i[1] != 0], explode=explode, autopct='%1.f%%')
            plt.tight_layout()
            plt.axis('equal')

        plt.savefig('img.png',  facecolor='#2C2F33', transparent=True, bbox_inches='tight')
        plt.clf()
        plt.cla()
        embed = discord.Embed(title=message, color=0x2C2F33)
        file = discord.File("img.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        await channel.send(file=file, embed=embed)

    async def average(self, channel):
        await channel.send("average is {}".format(round((sum(self.points)/len(self.points))*10)/10))

    async def stadev(self, channel):
        await channel.send("standard deviation is {}".format(round(statistics.stdev(self.points), 3)))

def load():
    in_file = open("scores.json", "r")
    a = json.load(in_file)
    in_file.close()
    res = []
    for i in a:
        new = score(i, a[i][1])
        new.max = a[i][2]
        for j in a[i][0]:
            new.add_point(j)
        res.append(new)
    global loaded
    loaded = True
    return res


loaded = False
scores = load()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(status=discord.Status.idle, activity=discord.Game(name='Use "score help" for a help page'))

@client.event
async def on_message(message):
    if message.author.guild_permissions.administrator and message.content.startswith("score create"):
        content = message.content[13:]
        for i in scores:
            if i.name == content and message.guild.id == i.serverid:
                await message.channel.send("score name already in use")
                break
        else:
            scores.append(score(content, message.guild.id))
            await message.channel.send("score {} created".format(content))
            save()

    if message.author.guild_permissions.administrator and message.content.startswith("score max"):
        content = message.content[10:].split(' ')
        for i in scores:
            if ''.join(content[1:]) == i.name and message.guild.id == i.serverid:
                i.max = int(content[0])
                await message.channel.send("score max set to {}".format(content[0]))
                save()
                break

    if message.author.guild_permissions.administrator and message.content.startswith("score rm"):
        content = message.content[9:].split(' ')
        print(message.content[9:].split(' '))
        for i in scores:
            if ''.join(content[1:]) == i.name and message.guild.id == i.serverid:
                i.rm_point(float(content[0]))
                await message.channel.send("score {} removed from {}!".format(content[0], i.name))
                save()

    if message.content.startswith("score add"):
        content = message.content[10:].split(' ')
        for i in scores:
            if ''.join(content[1:]) == i.name and message.guild.id == i.serverid:
                i.add_point(float(content[0]))
                await message.channel.send("score {} added to {}!".format(content[0], i.name))
                save()

    if message.content.startswith("score addlist"):
        content = message.content[14:].split(' ')
        for i in scores:
            if ''.join(content[1:]) == i.name and message.guild.id == i.serverid:
                for k in content[0].split(','):
                    i.add_point(float(k))
                await message.channel.send("score {} added to {}!".format(content[0], i.name))
                save()

    if message.content.startswith("score view"):
        content = message.content[11:]
        for i in scores:
            if i.name == content and message.guild.id == i.serverid:
                await i.render(message.channel)
                break

    if message.content.startswith("score view bar"):
        content = message.content[15:]
        for i in scores:
            if i.name == content and message.guild.id == i.serverid:
                await i.render(message.channel, 'bar')
                break

    if message.content.startswith("score view pie"):
        content = message.content[15:]
        for i in scores:
            if i.name == content and message.guild.id == i.serverid:
                await i.render(message.channel, 'pie')
                break

    if message.content.startswith("score average"):
        content = message.content[14:]
        for i in scores:
            if i.name == content and message.guild.id == i.serverid:
                await i.average(message.channel)
                break

    if message.content.startswith("score stdev"):
        content = message.content[12:]
        for i in scores:
            if i.name == content and message.guild.id == i.serverid:
                await i.stadev(message.channel)
                break

    if message.content == 'score help':
        embed = discord.Embed(title="scoreBot help page",
                              description="scoreBot is a bot that helps you track scores of tests/exams\nThe prefix is \'score \'", color=0x7289DA)
        embed.add_field(name="Commands", value="**create NAME** - to create new score with name (mods only)\n"
                                               "**max NUMBER NAME** - to set max result of NAME (mods only)\n"
                                               "**add RESULT NAME** - to add RESULT to NAME\n"
                                               "**rm RESULT NAME** - to remove 1 instance of RESULT from NAME (mods only)\n"
                                               "**addlist RESULT,RESULT,...,RESULT NAME** - to add list of results to NAME (mods only)\n"
                                               "**view NAME** - to view graph of NAME\n"
                                               "**view bar/pie NAME** - to view bar/piegraph of NAME\n"
                                               "**average NAME** - to get average result of NAME\n"
                                               "**stdev NAME** - to get standard deviation of NAME\n"
                                               "**score list** - to list all current scores", inline=True)

        await message.channel.send(embed=embed)

    if message.content == 'score list':
        text = ''
        for i in scores:
            if i.serverid == message.guild.id:
                text += '- {}\n'.format(i.name)
        embed = discord.Embed(title="List of current scores:",
                              description=text,
                              color=0x7289DA)
        await message.channel.send(embed=embed)

client.run(token)