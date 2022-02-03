<template>
  <div class="dropdown">
    <div
      @click="toggle"
      class="dropdown-input-container"
      :class="{ searchable: isSearchable, disabled: isDisabled }"
    >
      <input
        class="search"
        type="text"
        ref="search-input"
        @input="execUpdateValue($event.target.value)"
        :disabled="!isSearchable || !visible || isDisabled"
        :class="{ disabled: isDisabled }"
        :placeholder="isSearchable && visible ? nullDisplay : ''"
      />

      <div v-if="!isMulti" class="selected-items" :class="{ disabled: isDisabled }">
        <span v-show="!isMulti && !visible" class="selected-items__item">
          <span v-if="selectedItemsObject">{{ selectedItemsObject[displayKey] }}</span>
          <span v-else class="muted">{{ nullDisplay }}</span>
          <span
            @click.stop="execUpdateSelected(selectedItemsObject[valueKey])"
            class="selected-items__item__remove"
            v-if="selectedItemsObject"
            >x</span
          >
        </span>
      </div>
      <div
        v-if="isMulti && !isHidden && !visible"
        class="selected-items multi"
        :class="{ disabled: isDisabled }"
        @click.stop.prevent="toggle"
      >
        <span
          @click.stop.prevent="execUpdateSelected(item[valueKey])"
          :key="`${item[valueKey]}-${i}`"
          v-for="(item, i) in selectedItemsObject"
          class="selected-items__item"
        >
          {{ item[displayKey] }}
        </span>
      </div>
      <div
        v-if="isMulti && isHidden && !visible"
        class="selected-items"
        :class="{ disabled: isDisabled }"
        @click.stop.prevent="toggle"
      >
        <span v-show="isMulti && !visible" class="selected-items__item">
          <span class="muted">{{ nullDisplay }}</span>
        </span>
      </div>

      <slot name="dropdown-icon" v-if="showIcon" :classes="'dropdown-icon'">
        <span
          v-show="showIcon"
          class="dropdown-icon"
          :class="{ 'dropdown-icon__expanded': visible }"
        >
          <svg fill="black" stroke="black" width="15px" height="10px" viewBox="0 0 290 290">
            <use xlink:href="#arrow-down" />
          </svg>
        </span>
      </slot>
    </div>

    <div v-if="visible" class="dropdown-content">
      <template v-for="(item, i) in itemList">
        <slot
          :classes="'dd-item'"
          :name="`dd-item-${item[displayKey]}`"
          :data="item"
          :selectItem="execUpdateSelected"
        >
          <div
            :key="`${item[valueKey]}-${i}`"
            @click.prevent="execUpdateSelected(item[valueKey])"
            class="dd-item"
            :class="{
              selected: isMulti
                ? ~checkIsSelected(item[valueKey])
                : item[valueKey] == selectedItems,
            }"
          >
            {{ item[displayKey] }}
          </div>
        </slot>
      </template>

      <slot name="dd-pagination" :classes="'dd-item'" :loadMore="onLoadMore">
        <div v-if="hasNext" @click.stop class="dd-item">+</div>
      </slot>
    </div>
  </div>
</template>

<script>
/**
 * attrs:
 * @searchable determines if the items are searchable and shows input field
 * @multi determines if select is multi select:
 *        a. if it is it expects v-model to send an array
 *        b. does not close dropdown on select if multi select is enabled
 *        c. displays selected values differently and allows them to be removed on the fly
 *
 *@local enables local sorting for objects
 *@hide hides the list of selected items when multi is set
 * Props:
 *@has_next enables pagination
 *@inputDelay && @selectDelay optional debounce
 *@itemsRef .sync provide the object of the selected
 *          useful when this is populated with data saved in the server
 *          or if you would like the whole object returned rather than just the value
 *          must use .sync as the child will sync value back to parent when item is changed
 *@items the array or items as key value pair.
 *@valueKey && @displayKey by default value and key are used respectively but can be customized
 *@disabled to disable the dropdown menu
 *@closeOnSelect determines where the dropdwon will close after each select on a multi-select
 *
 *
 *
 *
 **/

import debounce from 'lodash.debounce'

export default {
  name: 'DropDownSelect',
  props: {
    showIcon: {
      type: Boolean,
      default: true,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    hasNext: {
      type: Boolean,
      default: false,
    },
    inputDelay: {
      type: Number,
      default: 100,
    },
    selectDelay: {
      type: Number,
      default: 100,
    },
    items: {
      /** list of items */

      type: Array,
    },
    displayKey: {
      /** Key of the displayValue */
      type: String,
      default: 'key',
    },
    idKey: {
      /** Key of an optional unique key */
      type: String,
    },
    valueKey: {
      /** Key of the Value of the selected item */
      type: String,
      default: 'value',
    },
    right: {
      type: Number,
      default: 0,
    },
    left: {
      type: Number,
      default: 0,
    },
    value: {},
    itemsRef: {
      type: [Object, Array],
    },
    nullDisplay: {
      type: String,
      default: 'Click to Select',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      visible: false,
      eventClicked: null,
      selectedItems: this.value,
      selectedItemsObject: null,
      execUpdateValue: debounce(this.updateValue, this.inputDelay),
      execUpdateSelected: debounce(this.updateSelectedValue, this.selectDelay),
      itemList: [],
      isLoading: this.loading,
    }
  },
  components: {},
  watch: {
    value: {
      immediate: true,
      handler(val) {
        this.selectedItems = val
        this.selectedItemsObject = this.itemsRef
      },
    },
    items: {
      deep: true,
      handler(val) {
        this.itemList = val
      },
    },
    visible: {
      immediate: true,
      handler(val) {
        if (val) {
          window.addEventListener('click', this.closeEvent)
        } else {
          this.removeEvent()
          if (this.$refs['search-input']) {
            this.$refs['search-input'].value = ''
          }
        }
      },
    },
  },

  computed: {
    element() {
      return this.$el
    },

    isMulti() {
      return this.$attrs.hasOwnProperty('multi')
    },
    isSearchable() {
      return this.$attrs.hasOwnProperty('searchable')
    },
    isLocalFilter() {
      return this.$attrs.hasOwnProperty('local')
    },
    isHidden() {
      return this.$attrs.hasOwnProperty('hidden')
    },
    isNullable() {
      return this.$attrs.hasOwnProperty('nullable')
    },
    isDisabled() {
      // will also check loading state in future
      return this.disabled
    },
    isCloseOnSelect() {
      return this.$attrs.hasOwnProperty('closeOnSelect')
    },
  },
  created() {
    this.selectedItemsObject = this.objectSelectedItems()
    /* immediately update itemsRef if an item is already set */

    this.emitUpdateItemsRef(this.selectedItemsObject)
    /* wait until created so that all the elements of the dom are ready */

    if (this.isMulti) {
      if (!Array.isArray(this.value)) {
        throw new Error(
          JSON.stringify({
            code: 'expected_array',
            message: 'Multi is selected expected value to be array',
          }),
        )
      }
      if (this.itemsRef && !Array.isArray(this.itemsRef)) {
        throw new Error(
          JSON.stringify({
            code: 'expected_array',
            message: 'Multi is selected expected value to be array',
          }),
        )
      }
    }
    // making a copy for local searching if enabled
    this.itemList = [...this.items]
  },
  methods: {
    objectSelectedItems() {
      if (!this.isMulti && !this.selectedItems) {
        return null
      } else if (this.isMulti && !this.selectedItems.length) {
        return null
      }
      if (this.isMulti) {
        let objectItems = []
        for (let i = 0; i <= this.selectedItems.length; i++) {
          // using for loop and findIndex to maintain order
          let index = this.itemList.findIndex((it) => it[this.valueKey] == this.selectedItems[i])
          if (~index) {
            objectItems.push(this.itemList[index])
          } else if (this.itemsRef) {
            // check to see if it is part of the passed refs (as it may be serversie)
            let index = this.itemsRef.findIndex((it) => it[this.valueKey] == this.selectedItems[i])
            if (~index) {
              objectItems.push(this.itemsRef[index])
            }
          }
        }
        return objectItems
      }
      return this.itemList.find((i) => i[this.valueKey] == this.selectedItems)
        ? this.itemList.find((i) => i[this.valueKey] == this.selectedItems)
        : this.itemsRef[this.valueKey] == this.selectedItems
        ? this.itemsRef
        : null
    },
    onLoadMore() {
      this.isLoading = true
      this.$emit('load-more')
    },
    checkIsSelected(itemValue) {
      /**
       * @itemValue itemValue to check
       * will be used to style multiselect if selected and remove item if selected
       */
      const index = this.selectedItems.findIndex((i) => i == itemValue)
      return index
    },
    updateValue(val) {
      if (this.visible == false) {
        this.visible = true
      }
      if (this.isLocalFilter) {
        this.isLoading = true
        let results = this.items.filter((i) => {
          return i[this.displayKey].toLowerCase().includes(val.toLowerCase())
        })

        this.itemList = results
      }
      this.emitSearch(val)
      this.isLoading = false
    },
    toggle() {
      if (this.isDisabled) {
        this.visible = false
        return
      }
      if (this.visible) {
        this.closeDropDownEvent()
      }
      if (!this.visible) {
        this.visible = true
      }

      if (this.isSearchable) {
        this.$refs['search-input'].disabled = false
        this.$refs['search-input'].focus()
      }
      if (!this.visible) {
        this.removeEvent()
      }
    },
    closeDropDownEvent() {
      if (this.$refs['search-input']) {
        this.$refs['search-input'].value = ''
      }

      this.visible = false

      this.$emit('close')
    },
    emitSearch(val) {
      this.$emit('search-term', val)
    },
    emitUpdateItemsRef(itemsRef) {
      this.$emit('update:itemsRef', itemsRef)
    },

    emitSelected() {
      this.$emit('input', this.selectedItems)
    },

    updateSelectedValue(itemValue) {
      this.isLoading = true
      if (this.isMulti) {
        const index = this.checkIsSelected(itemValue)

        if (~index) {
          this.selectedItems.splice(index, 1)
          this.selectedItemsObject.splice(index, 1)
        } else {
          this.selectedItems.push(itemValue)
          this.selectedItemsObject = this.objectSelectedItems()
        }

        if (this.isCloseOnSelect) {
          this.closeDropDownEvent()
        }
      } else if (this.selectedItems == itemValue) {
        this.selectedItems = null
        this.selectedItemsObject = null
        this.closeDropDownEvent()
      } else {
        this.selectedItems = itemValue
        this.selectedItemsObject = this.objectSelectedItems()
        this.closeDropDownEvent()
      }
      this.emitSelected()
      this.emitUpdateItemsRef(this.selectedItemsObject)
      this.isLoading = false
    },
    removeEvent() {
      /*
        Remove the event listener if the toggle is no longer visible to reduce the events triggered
        */

      if (this.visible == false) {
        return window.removeEventListener('click', this.closeEvent)
      }
      return window.addEventListener('click', this.closeEvent)
    },
    closeEvent(e) {
      if (this.element.contains(e.target) || this.element.contains(e.target.parentNode)) {
        return
      }
      this.closeDropDownEvent()
      this.visible = false
    },
  },
}
</script>

<style scoped lang="scss">
/*
Display dropdown relative to the component it is triggered by
*/
.dropdown {
  display: inline-block;
  width: 100%;
  position: relative;
  height: 100%;
}
/* keep content hidden by default until visible is true */

.dropdown-content {
  position: absolute;
  top: 40px;
  flex-direction: column;
  display: flex;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  background-color: white;
  left: 2px;
  z-index: 100;
  width: 100%;
  max-height: 400px;
  overflow-x: scroll;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* mozilla */
}
.dropdown-content::-webkit-scrollbar {
  display: none; /* chrome safari */
}

.selected {
  background-color: lightgreen;
  color: darkgreen;
}
::v-deep .tn-dropdown__selection-container:after {
  position: absolute;
  content: '';
  top: 17px;
  right: 1em;
  width: 0;
  height: 0;
  border: 5px solid transparent;
  border-color: rgb(173, 171, 171) transparent transparent transparent;
}
.dropdown-input-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  border: 1px solid black;
  cursor: pointer;
  &.searchable {
    cursor: default;
  }
  &.disabled {
    cursor: not-allowed;
  }

  .search,
  .selected-items {
    position: absolute;
    font-size: 12px;
    padding: 0.3rem 2rem;
    border-radius: 0;
    height: 99%;
    background-color: transparent;
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* mozilla */
    width: 95%;
    outline: none;
    &.disabled {
      cursor: not-allowed;
    }
  }
  .dropdown-icon {
    position: absolute;
    right: 0.4rem;

    &__expanded {
      /* animation: rotatetoggleicon forwards;
      animation-duration: 1s;
      animation-iteration-count: 1; */
    }
  }

  .selected-items::-webkit-scrollbar {
    display: none; /* chrome safari */
  }

  .search {
    height: 60%;
    border: none;
    min-height: 0;
    min-width: 0;
    &::placeholder {
      color: #808080;
    }
    &:disabled {
      cursor: pointer;
    }
    &.disabled {
      cursor: not-allowed;
    }
  }
}

.selected-items.multi {
  display: flex;
  overflow-x: scroll;
  height: 2rem;
  padding-top: 0px;
  max-width: 85%;

  > .selected-items__item {
    height: 100%;

    background-color: purple;
    text-align: center;
    border-radius: 5px;
    color: white;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 15%;
    min-width: 5rem;
    padding: 0 0.5rem;
    font-size: 10px;
    margin: 0rem 0.2rem;
    font-weight: bold;

    &:hover {
      cursor: pointer;
    }
  }
}
.selected-items {
  &:hover {
    cursor: pointer;
  }
  display: flex;
  padding-left: 5%;
  padding-right: 5%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  &__item {
    max-width: 95%;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    &__remove {
      position: absolute;
      right: 1.5rem;
      border-radius: 50%;
    }
  }
}

.dd-item {
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: black;
  text-decoration: none;
  color: inherit;
  height: 100%;
  padding: 1rem 1rem;

  min-height: 40px;
  justify-content: center;
  align-items: center;
  width: 100%;

  &:hover {
    cursor: pointer;
    background-color: #f4f7f9;
  }
}
.muted {
  // muted color is the same as placeholder color
  color: #808080;
}

@keyframes rotatetoggleicon {
  from {
  }
  to {
    transform: rotate(180deg);
  }
}
</style>
