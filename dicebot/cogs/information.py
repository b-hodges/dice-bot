from discord.ext import commands
from sqlalchemy.exc import IntegrityError

from . import util
from .util import m


class InformationCategory (util.Cog):
    @commands.group('information', aliases=['info'], invoke_without_command=True)
    async def group(self, ctx):
        '''
        Manages character information
        '''
        raise util.invalid_subcommand(ctx)

    @group.command()
    async def add(self, ctx, name: str, *, description: str):
        '''
        Adds an information block to the character

        Parameters:
        [name] the name of the new information block
        [description*] the text of the information block
        '''
        description = util.strip_quotes(description)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        info = m.Information(character_id=character.id, name=name, description=description)
        try:
            ctx.session.add(info)
            ctx.session.commit()
        except IntegrityError:
            ctx.session.rollback()
            info = None

        if info is not None:
            await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(info)))
        else:
            raise Exception('{} already has a information block named {}'.format(str(character), name))

    @group.command(ignore_extra=False)
    async def rename(self, ctx, name: str, new_name: str):
        '''
        Changes the name of an information block

        Parameters:
        [name] the name of the block to change
        [new_name] the new name of the block
        '''
        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        info = ctx.session.query(m.Information)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if info is None:
            raise util.ItemNotFoundError(name)

        try:
            info.name = new_name
            ctx.session.commit()
            await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(info)))
        except IntegrityError:
            ctx.session.rollback()
            raise Exception('{} already has an information block named {}'.format(str(character), new_name))

    @group.command(aliases=['desc'])
    async def description(self, ctx, name: str, *, description: str):
        '''
        Adds or updates the description for an information block

        Parameters:
        [name] the name of the block
        [description*] the new description for the block
            the description does not need quotes
        '''
        description = util.strip_quotes(description)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        info = ctx.session.query(m.Information)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if info is None:
            raise util.ItemNotFoundError(name)

        info.description = description
        ctx.session.commit()
        await util.send_embed(ctx, description='{} now has {}'.format(str(character), str(info)))

    @group.command(aliases=['rmdesc'])
    async def removedescription(self, ctx, *, name: str):
        '''
        Clears an information block's description

        Parameters:
        [name*] the name of the block to clear the description for
        '''
        name = util.strip_quotes(name)

        await ctx.invoke(self.description, name, description='')

    @group.command()
    async def check(self, ctx, *, name: str):
        '''
        Shows the information block

        Parameters:
        [name*] the name of the block
        '''
        name = util.strip_quotes(name)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)
        info = ctx.session.query(m.Information)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if info is None:
            raise util.ItemNotFoundError(name)
        text = '**{}**'.format(str(info))
        if info.description:
            text += '\n' + info.description
        await util.send_embed(ctx, description=text)

    @group.command(ignore_extra=False)
    async def list(self, ctx):
        '''
        Lists character's information
        '''
        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)
        await util.inspector(ctx, character, 'information', desc=True)

    @group.command(aliases=['delete'])
    async def remove(self, ctx, *, name: str):
        '''
        Removes an information block from the character
        This deletes all of the data associated with the block

        Parameters:
        [name*] the name of the block
        '''
        name = util.strip_quotes(name)

        character = util.get_character(ctx.session, ctx.author.id, ctx.guild.id)

        info = ctx.session.query(m.Information)\
            .filter_by(character_id=character.id, name=name).one_or_none()
        if info is None:
            raise util.ItemNotFoundError(name)

        ctx.session.delete(info)
        ctx.session.commit()
        await util.send_embed(ctx, description='{} removed'.format(str(info)))

    @group.command()
    async def inspect(self, ctx, *, name: str):
        '''
        Lists the information for a specified character

        Parameters:
        [name*] the name of the character to inspect
        '''
        name = util.strip_quotes(name)

        await util.inspector(ctx, name, 'information', desc=True)


def setup(bot):
    bot.add_cog(InformationCategory(bot))
