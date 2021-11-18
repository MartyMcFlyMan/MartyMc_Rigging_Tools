import maya.cmds as cmds


class AnimCurve:
    """ Works on selection so you must select keys for certain methods to work"""
    def __init__(self, name, attribute):
        self.name = name
        self.attribute = attribute
        self.animCurve_name = cmds.keyframe(q=True, n=True)[0]

        # queried values
        self.value_sel = cmds.keyframe(sl=True, q=True, vc=True)
        self.time_sel = cmds.keyframe(sl=True, q=True)
        self.keys_sel = cmds.keyframe(sl=True, q=True, keyframeCount=True)
        self.__key_index_list = cmds.keyframe(sl=True, q=True, iv=True)

    @property
    def time_all(self):
        """get time values of all keys"""
        return cmds.keyframe(self.attribute, q=True)

    @property
    def val_all(self):
        """get value of all keys"""
        return cmds.keyframe(self.attribute, q=True, vc=True)

    @property
    def index_all(self):
        """get index of all keys"""
        key_index_list = cmds.keyframe(self.attribute, q=True, iv=True)
        return [int(x) for x in key_index_list]  # change index data type from Long to int

    @property
    def index_sel(self):
        """get index of selected keys"""
        return [int(x) for x in self.__key_index_list]  # change index data type from Long to int

    @property
    def keys_total(self):
        """get number of keys on attribute"""
        return cmds.keyframe(self.attribute, q=True, keyframeCount=True)

    @property
    def last_key(self):
        """get last key on attribute"""
        return self.keys_total - 1

    @property
    def last_key_sel(self):
        """get last key on attribute"""
        return self.index_sel[-1]

    @property
    def first_key(self):
        """get first key on attribute"""
        return self.index_all[0]

    @property
    def first_key_sel(self):
        """get first key in selection"""
        return self.index_sel[0]

    @staticmethod
    def get_dict(key, value):
        """get a dictionnary of the values of the two parameters you need.
        The function will work with any two lists of the same length.
        eg. the arguments (self.time_sel, self.value_sel)
        would give you a time:value dict of the selected keys"""
        key_value_dict = {}
        if len(key) == len(value):
            for i in range(len(key)):
                key_value_dict[key[i]] = value[i]
            return key_value_dict

        else:
            print "Error: The length of {} and {} do not match\ncannot create dictionary".format(key, value)
            return None

    def get_value_from_index(self, key_index):
        return cmds.keyframe(self.attribute, index=(key_index, key_index), q=True, vc=True)[0]

    def animcurve_info(self):
        print '\n----------------------------------------'
        print 'Object informations:\n'
        print 'Object name:', self.name
        print 'Keyed attribute:', self.attribute
        print 'animCurve node name:', self.animCurve_name

        print '\nKeyframe informations:\n'
        print 'Selected keys values:', self.value_sel
        print 'All key values:', self.val_all
        print 'Selected keys time values:', self.time_sel
        print 'All keys time values:', self.time_all
        print 'Selected keys indexes:', self.index_sel
        print 'All key indexes:', self.index_all
        print 'Number of keys in selection:', self.keys_sel
        print 'Total keys on attribute:', self.keys_total
        print 'Index of the last key on the attribute:', self.last_key
        print 'Index of the last key in selection:', self.last_key_sel
        print 'Index of the first key on the attribute:', self.first_key
        print 'Index of the first key in selection:', self.first_key_sel
        print '\nget_dict examples:'
        print 'index:value dict:', self.get_dict(self.time_sel, self.value_sel)
        print 'time:value dict:', self.get_dict(self.time_sel, self.value_sel)
        print '----------------------------------------'

    def get_backward_difference(self, index):
        previous_index = index - 1
        print 'index:', index
        print 'prev index:', previous_index

        index_value_dict = self.get_dict(self.index_all, self.val_all)
        print 'dict:', index_value_dict

        previous_value = self.get_value_from_index(previous_index)
        print 'prev value', previous_value
        current_value = self.get_value_from_index(index)
        print 'current val', current_value

        return current_value - previous_value

    def get_forward_difference(self, index):
        return




