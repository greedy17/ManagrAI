<template>
  <div class="dropdown">
    <div @click="toggle" class="dropdown-input-container" :class="{ searchable: isSearchable }">
      <input
        class="search"
        type="text"
        @input="
          visible = true
          execUpdateValue($event.target.value)
        "
        :disabled="!isSearchable"
        @blur="$event.target.value = ''"
        @focus="visible = true"
      />
      <div v-if="!isMulti" class="selected-items">
        <span v-show="!isMulti && !visible">
          {{ objectSelectedItems ? objectSelectedItems[displayKey] : '' }}</span
        >
      </div>
      <div v-if="isMulti && !isHidden" class="selected-items multi">
        <span
          @click.prevent="execUpdateSelected(item[valueKey])"
          :key="`${item[valueKey]}-${i}`"
          v-for="(item, i) in objectSelectedItems"
          class="selected-items__item"
        >
          {{ item[displayKey] }}
        </span>
      </div>
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
        <div v-if="hasNext" @click.prevent="onLoadMore" class="dd-item">
          +
        </div>
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
 *@local enables local sorting for objects required to use sync when passing items :items.sync
 *@hide hides the list of selected items when multi is set
 *
 *
 *
 *
 *
 **/

import debounce from 'lodash.debounce'
export default {
  name: 'DropDownSelect',
  props: {
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
      default: 0,
    },
    selectDelay: {
      type: Number,
      default: 0,
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
  },
  data() {
    return {
      visible: false,
      eventClicked: null,
      selectedItems: this.value,
      execUpdateValue: debounce(this.updateValue, this.inputDelay),
      execUpdateSelected: debounce(this.updateSelectedValue, this.selectDelay),
      itemList: [],
      isLoading: this.loading,
    }
  },
  watch: {
    items: {
      deep: true,
      handler(val) {
        this.itemList = val
      },
    },
  },

  computed: {
    element() {
      return this.$el
    },
    objectSelectedItems() {
      if (!this.selectedItems) {
        return null
      }
      if (this.isMulti) {
        return this.selectedItems.map(v => {
          return this.itemList.filter(i => i[this.valueKey] == v)[0]
        })
      }
      return this.itemList.filter(i => i[this.valueKey] == this.selectedItems)[0]
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
  },
  created() {
    /* wait until created so that all the elements of the dom are ready */
    window.addEventListener('click', this.closeEvent)
    if (this.isMulti) {
      if (!Array.isArray(this.value)) {
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
    onLoadMore() {
      this.isLoading = true
      this.$emit('load-more')
    },
    checkIsSelected(itemValue) {
      /**
       * @itemValue itemValue to check
       * will be used to style multiselect if selected and remove item if selected
       */
      const index = this.selectedItems.findIndex(i => i == itemValue)
      return index
    },
    updateValue(val) {
      if (this.visible == false) {
        this.visible = true
      }
      if (this.isLocalFilter) {
        this.isLoading = true
        let results = this.items.filter(i => {
          return i[this.displayKey].toLowerCase().includes(val.toLowerCase())
        })

        this.itemList = results
      }
      this.emitSearch(val)
      this.isLoading = false
    },
    toggle() {
      this.visible = !this.visible
    },
    closeDropDownEvent() {
      this.$emit('close')
    },
    emitSearch(val) {
      this.$emit('search-term', val)
    },
    emitUpdateItems(items) {
      this.$emit('update:items', items)
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
        } else {
          this.selectedItems.push(itemValue)
        }
      } else {
        this.selectedItems = itemValue
        this.visible = false
      }
      this.emitSelected(itemValue)
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
      if (this.element.contains(e.target) !== true) {
        this.closeDropDownEvent()
        this.visible = false
      }
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
  background-color: #e5f2ea;
  color: darkgreen;
}

.dropdown-input-container {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  &.searchable {
    cursor: default;
  }
  border-radius: 5px;
  padding: 0.5rem 0.5rem;

  .search,
  .selected-items {
    position: absolute;
    top: 0;
    left: 0;
    -ms-overflow-style: none; /* IE and Edge */
    scrollbar-width: none; /* mozilla */
  }
  .selected-items::-webkit-scrollbar {
    display: none; /* chrome safari */
  }

  .search {
    width: 100%;
    height: 100%;
    border: none;
    padding-top: 2%;
    &:disabled {
      cursor: pointer;
    }
  }
}

.selected-items.multi {
  display: flex;
  overflow-y: scroll;
  height: 2rem;
  padding: 0px;
  > .selected-items__item {
    margin: 0.2rem;
    background-color: purple;
    border-radius: 2px;
    color: white;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 10%;
    padding: 0rem 0.2rem;
    font-size: 10px;
    font-weight: bold;
    &:hover {
      cursor: pointer;
    }
  }
}
.selected-items {
  width: 100%;
  display: flex;
  overflow-y: scroll;
  //max-height: 20px;
  padding-left: 10px;
  padding-top: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dd-item {
  display: inline-flex;
  overflow: hidden;
  white-space: nowrap;
  color: black;
  text-decoration: none;
  color: inherit;
  height: 100%;
  border-bottom: 1px solid lightgray;
  min-height: 40px;
  justify-content: center;
  align-items: center;
  &:hover {
    cursor: pointer;
    background-color: lighten(gray, 20%);
  }
}
</style>
