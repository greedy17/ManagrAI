<template>
  <div class="dropdown">
    <div class="dropdown-container">
      <slot :classes="'dd-button'" :toggle="toggle" name="dropdown-trigger">
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
 *
 *
 * @vue-prop {loading} loading state
 * @vue-prop {items} list of key value pairs for the dropdown content
 * @vue-prop {displayKey} the key of the display value, if none provided 'key' will be used
 *
 * @vue-prop {idKey} the key of the id value, if none provided 'id' will be used
 * @vue-prop {valueKey} the key of the value value, if none provided 'id' will be used
 * @vue-prop {right} alignment from right
 * @vue-prop {left} alignment from left
 *
 * @vue-slot {dd-button} slot to override default icon
 *
 * @vue-slot-values {classes, toggle} passed back to the slot for re-use
 **/

export default {
  name: 'DropDownMenu',
  props: {
    loading: {
      type: Boolean,
      default: false,
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
  watch: {
    visible() {
      this.removeEvent()
    },
  },
  computed: {
    element() {
      return this.$el
    },
  },
  created() {},
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
