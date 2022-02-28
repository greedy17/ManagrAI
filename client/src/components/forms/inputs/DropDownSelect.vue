<template>
  <div class="dropdown">
    <div class="dropdown-container">
      <div @click="toggle" class="dropdown-input-container" :class="{ searchable: isSearchable }">
        <input
          class="search"
          type="text"
          @input="execUpdateValue($event.target.value)"
          :disabled="!isSearchable"
        />
        <div v-if="!isMulti" class="selected-items">
          <span v-show="!isMulti && !visible">
            {{ objectSelectedItems ? objectSelectedItems[displayKey] : '' }}
          </span>
        </div>
        <div v-if="isMulti" class="selected-items multi">
          <span
            @click.prevent="execUpdateSelected(item[valueKey])"
            :key="`${item[valueKey]}-${i}`"
            v-for="(item, i) in objectSelectedItems"
            class="selected-items__item"
            >{{ item[displayKey] }}</span
          >
        </div>
      </div>

      <div
        v-if="visible && (isLoading || loading)"
        class="dropdown-content"
        :style="{
          right: right > 0 ? `${right}px` : false,
          left: left > 0 ? `${left}px` : false,
          display: visible ? 'flex' : 'none',
        }"
      >
        <div class="loading-container">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
      </div>
      <div
        v-if="visible && !isLoading && !loading"
        class="dropdown-content"
        :style="{
          right: right > 0 ? `${right}px` : false,
          left: left > 0 ? `${left}px` : false,
          display: visible ? 'flex' : 'none',
        }"
      >
        <template v-for="(item, i) in items">
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
          <div v-if="hasNext" @click.prevent="onLoadMore" class="dd-item">+</div>
        </slot>
      </div>
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
 *
 *
 *
 *
 *
 *
 **/

import isPlainObject from 'lodash.isplainobject'
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

  computed: {
    element() {
      return this.$el
    },
    objectSelectedItems() {
      if (!this.selectedItems) {
        return null
      }
      if (this.isMulti) {
        return this.selectedItems.map((v) => {
          return this.itemList.filter((i) => i[this.valueKey] == v)[0]
        })
      }
      return this.itemList.filter((i) => i[this.valueKey] == this.selectedItems)[0]
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
      const index = this.selectedItems.findIndex((i) => i == itemValue)
      return index
    },
    updateValue(val) {
      if (this.visible == false) {
        this.visible = true
      }
      if (this.isLocalFilter) {
        this.isLoading = true

        let results = this.itemList.filter((i) => {
          return i[this.displayKey].toLowerCase().includes(val)
        })

        this.emitUpdateItems(results)
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

    emitSelected(item) {
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
  position: relative;
  display: inline-block;
  min-width: 200px;
}
/* keep content hidden by default until visible is true */

.dropdown-content {
  position: absolute;
  flex-direction: column;
  justify-content: space-evenly;
  min-width: 160px;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
  background-color: white;
  top: 40px;
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

.dropdown-input-container {
  cursor: pointer;
  &.searchable {
    cursor: default;
  }
  border-radius: 5px;
  padding: 0.5rem 0.5rem;
  position: relative;
  width: 100%;
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
    border: none;
    min-height: 20px;
    padding-top: 15px;
    width: 100%;
    &:disabled {
      cursor: pointer;
    }
  }
}

.selected-items.multi {
  width: 100%;
  display: flex;
  overflow-y: scroll;
  max-height: 20px;
  padding: 0px;
  > .selected-items__item {
    margin: 0.2rem;
    background-color: purple;
    border-radius: 2px;
    color: white;
    min-width: 40px;
    padding: 0rem 0.2rem;
    font-size: 8px;
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
  max-height: 20px;
  padding-left: 10px;
  padding-top: 10px;
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

.loading-container {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 80px;
}
.loading-container div {
  position: absolute;
  top: 33px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: darkgray;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.loading-container div:nth-child(1) {
  left: 8px;
  animation: loading-container1 0.6s infinite;
}
.loading-container div:nth-child(2) {
  left: 8px;
  animation: loading-container2 0.6s infinite;
}
.loading-container div:nth-child(3) {
  left: 32px;
  animation: loading-container2 0.6s infinite;
}
.loading-container div:nth-child(4) {
  left: 56px;
  animation: loading-container3 0.6s infinite;
}
@keyframes loading-container1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes loading-container3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}
@keyframes loading-container2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(24px, 0);
  }
}
</style>
