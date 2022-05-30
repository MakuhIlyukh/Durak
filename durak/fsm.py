# %%
from transitions import Machine
import random


class NarcolepticSuperhero(object):

    # Define some states. Most of the time, narcoleptic superheroes are just like
    # everyone else. Except for...
    states = ['asleep', 'hanging out', 'hungry', 'sweaty', 'saving the world']

    def __init__(self, name):

        # No anonymous superheroes on my watch! Every narcoleptic superhero gets
        # a name. Any name at all. SleepyMan. SlumberGirl. You get the idea.
        self.name = name

        # What have we accomplished today?
        self.kittens_rescued = 0

        # Initialize the state machine
        self.machine = Machine(model=self,
                               states=NarcolepticSuperhero.states,
                               initial='asleep')

        # Add some transitions. We could also define these using a static list of
        # dictionaries, as we did with states above, and then pass the list to
        # the Machine initializer as the transitions= argument.

        # At some point, every superhero must rise and shine.
        self.machine.add_transition(trigger='wake_up',
                                    source='asleep',
                                    dest='hanging out')

        # Superheroes need to keep in shape.
        self.machine.add_transition('work_out',
                                    'hanging out',
                                    'hungry')

        # Those calories won't replenish themselves!
        self.machine.add_transition('eat',
                                    'hungry',
                                    'hanging out')

        # Superheroes are always on call. ALWAYS. But they're not always
        # dressed in work-appropriate clothing.
        self.machine.add_transition('distress_call',
                                    '*',
                                    'saving the world',
                                    before='change_into_super_secret_costume')

        # When they get off work, they're all sweaty and disgusting. But before
        # they do anything else, they have to meticulously log their latest
        # escapades. Because the legal department says so.
        self.machine.add_transition('complete_mission',
                                    'saving the world',
                                    'sweaty',
                                    after='update_journal')

        # Sweat is a disorder that can be remedied with water.
        # Unless you've had a particularly long day, in which case... bed time!
        self.machine.add_transition('clean_up',
                                    'sweaty',
                                    'asleep',
                                    conditions=['is_exhausted'])
        self.machine.add_transition('clean_up',
                                    'sweaty',
                                    'hanging out')

        # Our NarcolepticSuperhero can fall asleep at pretty much any time.
        self.machine.add_transition('nap',
                                    '*',
                                    'asleep')

    def update_journal(self):
        """ Dear Diary, today I saved Mr. Whiskers. Again. """
        self.kittens_rescued += 1

    @property
    def is_exhausted(self):
        """ Basically a coin toss. """
        return random.random() < 0.5

    def change_into_super_secret_costume(self):
        print("Beauty, eh?")


# %%
batman = NarcolepticSuperhero("Batman")
batman.state


# %%
batman.wake_up()
batman.state


# %%
batman.nap()
batman.state


# %%
batman.clean_up()


# %%
batman.wake_up()
batman.work_out()
batman.state


# %%
# Batman still hasn't done anything useful...
batman.kittens_rescued


# %%
# We now take you live to the scene of a horrific kitten entreement...
batman.distress_call()


# %%
batman.state


# %%
# Back to the crib.
batman.complete_mission()
batman.state


# %%
batman.clean_up()
batman.state


# %%
# Another productive day, Alfred.
batman.kittens_rescued


# %%
class A:
    def __init__(self):
        self._machine = Machine(
            self,
            states=[{"name": "sleep",
                     "on_enter": "foo"}],
            initial="sleep")
    
    def foo(self):
        print("foo!!!")

# %%
a = A()
a.state

# %%
a._machine.set_state("sleep")

# %%
a.to_sleep()


# %%
class A:
    def __init__(self):
        self._machine = Machine(self, ["A", "B"], initial="A")
        self._machine.add_transition('heat', 'A', 'B', conditions='cond')
    
    def cond(self):
        return False

# %%
a = A()

# %%
a.heat()

# %%
a.state

# %%
a.transitions


# %%
class A:
    def __init__(self):
        self._machine = Machine(self, ["A", "B"], initial="A")
        self._machine.add_transition('heat', 'A', 'B', conditions=['cond', 'cond2'])

    def cond(self, t):
        return t > 0
    
    def cond2(self):
        return True


a = A()
a.heat(5)
# %%



# %%
