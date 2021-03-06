from discord.ext import commands
from sqlalchemy.exc import IntegrityError

from . import util
from .util import m


class SpellCategory (util.Cog):
    @commands.group('spell', invoke_without_command=True)
    async def group(self, ctx):
        '''
        Manage character spell list
        '''
        raise util.invalid_subcommand(ctx)

    @group.command(aliases=['update'], ignore_extra=False)
    async def add(self, ctx, name: str, level: int):
        '''
        Adds/updates a new spell for a character

        Parameters:
        [name] name of spell to store
        [level] the level of the spell
        '''
        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        spell = util.sql_update(ctx.session, m.Spell, {
            'character': character,
            'name': name,
        }, {
            'level': level,
        })

        await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(spell)))

    @group.command(ignore_extra=False)
    async def rename(self, ctx, name: str, new_name: str):
        '''
        Changes the name of a spell

        Parameters:
        [name] the name of the spell to change
        [new_name] the new name of the spell
        '''
        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        spell = ctx.session.query(m.Spell)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if spell is None:
            raise util.ItemNotFoundError(name)

        try:
            spell.name = new_name
            ctx.session.commit()
            await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(spell)))
        except IntegrityError:
            ctx.session.rollback()
            raise Exception('{} already has a spell named {}'.format(str(character), new_name))

    @group.command()
    async def setlevel(self, ctx, level: int, *, name: str):
        '''
        Changes the level of a spell

        Parameters:
        [level] the new level of the spell
        [name*] the name of the spell
        '''
        name = util.strip_quotes(name)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        spell = ctx.session.query(m.Spell)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if spell is None:
            raise util.ItemNotFoundError(name)

        spell.level = level
        ctx.session.commit()
        await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(spell)))

    @group.command(aliases=['desc'])
    async def description(self, ctx, name: str, *, description: str):
        '''
        Adds or updates a description for a spell

        Parameters:
        [name] the name of the spell
        [description*] the new description for the spell
            the description does not need quotes
        '''
        description = util.strip_quotes(description)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        spell = ctx.session.query(m.Spell)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if spell is None:
            raise util.ItemNotFoundError(name)

        spell.description = description
        ctx.session.commit()
        await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(spell)))

    @group.command(aliases=['rmdesc'])
    async def removedescription(self, ctx, *, name: str):
        '''
        Removes a spell's description

        Parameters:
        [name*] the name of the spell to remove the description from
        '''
        name = util.strip_quotes(name)

        await ctx.invoke(self.description, name, description=None)

    @group.command()
    async def check(self, ctx, *, name: str):
        '''
        Checks the status of a spell

        Parameters:
        [name*] the name of the spell
        '''
        name = util.strip_quotes(name)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)
        spell = ctx.session.query(m.Spell)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if spell is None:
            raise util.ItemNotFoundError(name)
        text = '**{}**'.format(str(spell))
        if spell.description:
            text += '\n' + spell.description
        await util.send_embed(ctx, description=text)

    @group.command(ignore_extra=False)
    async def list(self, ctx):
        '''
        Lists all of a character's spells
        '''
        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)
        await util.inspector(ctx, character, 'spells', desc=True)

    @group.command(ignore_extra=False)
    async def level(self, ctx, level: int):
        '''
        Lists all of a character's spells of a given level

        Parameters:
        [level] the level of spells to show
        '''
        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)
        spells = ctx.session.query(m.Spell)\
            .filter_by(character_id=character.id, level=level)\
            .order_by(m.Spell.name).all()
        text = ["{}'s spells:".format(character.name)]
        for spell in spells:
            text.append(str(spell))
        await util.send_embed(ctx, description='\n'.join(text))

    @group.command(aliases=['delete'])
    async def remove(self, ctx, *, name: str):
        '''
        Deletes a spell from the character

        Parameters:
        [name*] the name of the spell
        '''
        name = util.strip_quotes(name)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        spell = ctx.session.query(m.Spell)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if spell is None:
            raise util.ItemNotFoundError(name)

        ctx.session.delete(spell)
        ctx.session.commit()
        await util.send_embed(ctx, description='{} no longer has {}'.format(str(character), str(spell)))

    @group.command()
    async def inspect(self, ctx, *, name: str):
        '''
        Lists the spells for a specified character

        Parameters:
        [name*] the name of the character to inspect
        '''
        name = util.strip_quotes(name)

        await util.inspector(ctx, name, 'spells', desc=True)


def setup(bot):
    bot.add_cog(SpellCategory(bot))
