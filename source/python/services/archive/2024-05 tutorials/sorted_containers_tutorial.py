#!/usr/bin/env python
# coding: utf-8

# # About
# ```This tutorial was made for you by Mark Lidenberg @marklidenberg, 2022.08.30```

# # SortedContainers - sorted python objects. Written in pure python, fast as C-extensions
#
# - https://github.com/grantjenks/python-sortedcontainers
#
# You can run this notebook out-of-the-box
#
# Сортированные списки полезны тем, что по ним можно быстро делать поиск (за log(N), бинарный поиск)

# In[ ]:


# !pip install sortedcontainers


#

# In[ ]:


import pandas as pd

from sortedcontainers import SortedDict, SortedList, SortedSet


# # SortedList
# - Sorted list is a sorted mutable sequence.
# - Sorted list values are maintained in sorted order.
# - Sorted list values must be comparable. The total ordering of values must not change while they are stored in the sorted list.
#
#

# ## Init and add values

# In[ ]:


sorted_list = SortedList([3, 1, 2, 5, 4])
sorted_list, list(sorted_list)


# In[ ]:


sorted_list.add(3.5)  # returns None
sorted_list


# In[ ]:


sorted_list.update([1.5, 2.5])  # returns None
sorted_list


# ## Remove elements

# In[ ]:


# remove element safely
sorted_list.discard(2.5)  # returns None
sorted_list.discard(-1)  # returns None
sorted_list


# In[ ]:


# remove element unsafely
sorted_list.remove(1.5)  # returns None
try:
    sorted_list.remove(-1)  # Will raise ValueError, since -1 is not in list
except Exception as e:
    assert type(e) == ValueError
sorted_list


# In[ ]:


# remove last element
sorted_list.pop()  # returns last element
sorted_list.pop(index=2)  # == del sorted_list[2]
sorted_list


# In[ ]:


sorted_list.clear()  # returns None
sorted_list


# ## Fast lookups

# In[ ]:


sorted_list = SortedList("abbcccddddeeeee")


# In[ ]:


assert "f" not in sorted_list  # log(N)
assert sorted_list.count("e") == 5
assert sorted_list.index("c") == 3


# In[ ]:


sorted_list[3], sorted_list[6:10]


# In[ ]:


sorted_list.bisect_left("d"), sorted_list.bisect_right("d")


# In[ ]:


sorted_list = SortedList([10, 11, 11, 11, 12])
dataframe_values = []
for search_value in [-100, 10, 10.5, 11, 12, 100]:
    dataframe_values.append(
        [search_value, sorted_list.bisect_left(search_value), sorted_list.bisect_right(search_value)]
    )
pd.DataFrame(
    dataframe_values,
    columns=["search_value", "bisect_left: leftmost place to insert", "bisect_right: rightmost place to insert"],
)


# In[ ]:


sorted_list = SortedList("acegi")


# In[ ]:


list(sorted_list.irange("b", "h"))  # from b to h


# ## Operations

# In[20]:


sorted_list = SortedList("abc")


# In[21]:


sorted_list + sorted_list


# In[22]:


sorted_list * 3


# In[23]:


sorted_list += "de"
sorted_list


# In[24]:


sorted_list *= 2
sorted_list


# ## What you CAN'T do

# In[25]:


sorted_list = SortedList("abcde")


# In[26]:


try:
    sorted_list[2] = "c"
except Exception as e:
    print(e)


# In[27]:


try:
    sorted_list.reverse()
except Exception as e:
    print(e)


# In[28]:


try:
    sorted_list.append("f")
except Exception as e:
    print(e)


# In[29]:


try:
    sorted_list.extend(["f", "g", "h"])
except Exception as e:
    print(e)


# In[30]:


try:
    sorted_list.insert(5, "f")
except Exception as e:
    print(e)


# ## Custom key

# In[31]:


sorted_list = SortedList([3, 1, 2, 5, 4], key=lambda value: -value)
sorted_list


# # SortedDict
# - Sorted dict is a sorted mutable mapping.
# - Sorted dict keys are maintained in sorted order. The design of sorted dict is simple: sorted dict inherits from dict to store items and maintains a sorted list of keys.
# - Sorted dict keys must be hashable and comparable. The hash and total ordering of keys must not change while they are stored in the sorted dict.

# ## Works as dict as expected

# In[32]:


sorted_dict = SortedDict()
sorted_dict["e"] = 5
sorted_dict["b"] = 2
sorted_dict.update({"d": 4, "c": 3})
sorted_dict.setdefault("a", 1)


# In[33]:


d = {"alpha": 1, "beta": 2}
assert SortedDict([("alpha", 1), ("beta", 2)]) == d
assert SortedDict({"alpha": 1, "beta": 2}) == d
assert SortedDict(alpha=1, beta=2) == d


# In[34]:


sorted_dict = SortedDict({1: "one", 2: "two"})
sorted_dict


# ## Pop and peek

# In[35]:


sorted_dict = SortedDict({1: "one", 2: "two", 3: "three"})


# In[36]:


sorted_dict.popitem(index=-1), sorted_dict


# In[37]:


sorted_dict.peekitem(index=-1), sorted_dict


# ## Lookups

# In[38]:


sorted_dict = SortedDict(zip("abcde", "abcde".upper()))
sorted_dict


# In[39]:


assert sorted_dict.bisect_right("b") == 2
assert sorted_dict.index("a") == 0


# In[40]:


list(sorted_dict.irange("b", "z"))


# ## .keys(), .values(), .items() are special classes, but support indexing fluently

# In[41]:


sorted_dict.keys(), sorted_dict.values(), sorted_dict.items()


# In[42]:


sorted_dict.keys()[2]


# ## Custom sorting key

# In[43]:


sorted_dict = SortedDict(lambda value: -value, enumerate("abc", start=1))
sorted_dict


# ## Default sorted dict

# In[44]:


class DefaultSortedDict(SortedDict):
    def __missing__(self, key):
        return 0


default_sorted_dict = DefaultSortedDict()
default_sorted_dict["z"]


# # SortedSet
# - Sorted set uses Python’s built-in set for set-operations and maintains a sorted list of values

# ## Works like python set

# In[45]:


abcd = SortedSet("abcd")
cdef = SortedSet("cdef")
abcd, cdef


# In[46]:


abcd.difference(cdef)


# In[47]:


abcd.intersection(cdef)


# In[48]:


abcd.symmetric_difference(cdef)


# In[49]:


abcd.union(cdef)


# In[50]:


abcd | cdef


# In[51]:


abcd |= cdef


# In[52]:


abcd


# ## Works like SortedList

# In[53]:


sorted_set = SortedSet()
sorted_set.add("c")  # returns None
sorted_set.add("a")  # returns None
sorted_set.add("b")  # returns None

assert list(sorted_set) == ["a", "b", "c"]

# safe remove
sorted_set.discard("a")
# unsafe remove
sorted_set.remove("b")

try:
    sorted_set.remove("z")
except Exception as e:
    assert type(e) == KeyError

sorted_set


# In[54]:


sorted_set.update("def"), sorted_set  # NOTE: returns sorted set! This behavior is different from SortedList here
