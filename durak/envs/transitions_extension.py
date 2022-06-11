from functools import partial

from transitions import Machine, EventData


class MayMachine(Machine):
    def _can_trigger(self, model, trigger, *args, **kwargs):
        evt = EventData(None, None, self, model, args, kwargs)
        state = self.get_model_state(model).name

        for trigger_name in self.get_triggers(state):
            if trigger_name != trigger:
                continue
            for transition in self.events[trigger_name].transitions[state]:
                try:
                    _ = self.get_state(transition.dest)
                except ValueError:
                    continue
                self.callbacks(self.prepare_event, evt)
                self.callbacks(transition.prepare, evt)
                if all(c.check(evt) for c in transition.conditions):
                    return True
        return False

    def _add_may_transition_func_for_trigger(self, trigger, model):
        self._checked_assignment(model, "may_%s" % trigger, partial(self._can_trigger, model, trigger))

    def _add_trigger_to_model(self, trigger, model):
        # ???: Может лучше убрать следующую строку и добавить super()._add_trigger_to_model?
        self._checked_assignment(model, trigger, partial(self.events[trigger].trigger, model))
        self._add_may_transition_func_for_trigger(trigger, model)