<template>
  <div class="dropdown">
    <div class="dropdown-container">
      <slot :classes="'dd-button'" :selected="toggle" name="dropdown-trigger">
        <button class="dd-button" @click="toggle">
          <svg class="dd-icon" viewBox="0 0 24 24">
            <use xlink:href="@/assets/images/dropdown-arrow.svg#caret" />
          </svg>
        </button>
      </slot>
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
          :selectItem="emitSelected"
        >
          <div
            :key="`${item[valueKey]}-${i}`"
            @click.prevent="emitSelected(item[valueKey])"
            class="dd-item"
          >
            {{ item[displayKey] }}
          </div>
        </slot>
      </template>
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

export default {
  name: 'DropDownSelect',
  props: {
    loading: {
      type: Boolean,
      default: false,
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
  },
  data() {
    return {
      visible: false,
      eventClicked: null,
      isLoading: this.loading,
      selectedItem: null,
    }
  },
  computed: {
    element() {
      return this.$el
    },
  },
  created() {
    /* wait until created so that all the elements of the dom are ready */
    window.addEventListener('click', this.closeEvent)
  },
  methods: {
    toggle() {
      this.visible = !this.visible
    },
    closeDropDownEvent() {
      this.$emit('close')
    },
    onSelectedItem(item) {
      this.selectedItem = item
    },
    emitSelected(item) {
      this.visible = false
      this.$emit('selectedItem', item)
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
}
.dd-button {
  border: none;
  background-color: transparent;
  outline: none;
  &:hover {
    cursor: pointer;
  }
  > .dd-icon {
    width: 15px;
    height: 15px;
    fill: #484a6e;
  }
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
