<template>
  <label class="toggle">
    <input type="checkbox" class="toggle" :checked="checked" @click="emitToggle" />
    <div>
      <div></div>
    </div>
  </label>
</template>

<script>
export default {
  name: 'ToggleCheckBox',
  props: {
    checked: {
      required: true,
      type: Boolean,
    },
    eventToEmit: {
      required: true,
      type: String,
    },
  },
  methods: {
    emitToggle() {
      this.$emit(this.eventToEmit)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

$active-color: $dark-green;

label.toggle {
  cursor: pointer;
  height: auto;
  width: auto;
}

input[type='checkbox'].toggle {
  display: none;
}
// Normal Track
input[type='checkbox'].toggle + div {
  vertical-align: middle;
  width: 40px;
  height: 20px;
  border-radius: 999px;
  background-color: $soft-gray;
  transition-duration: 0.4s;
  transition-property: background-color, box-shadow;
  box-shadow: inset 0 0 0 0px rgba(0, 0, 0, 0.4);
}

// Checked Track (Green)
input[type='checkbox'].toggle:checked + div {
  width: 40px;
  background-position: 0 0;
  background-color: $active-color;
}

// Normal Knob
input[type='checkbox'].toggle + div > div {
  float: left;
  width: 18px;
  height: 18px;
  border-radius: inherit;
  background: #ffffff;
  transition-timing-function: cubic-bezier(0.54, 1.85, 0.5, 1);
  transition-duration: 0.4s;
  transition-property: transform, background-color, box-shadow;
  transition-timing-function: cubic-bezier(0.54, 1.85, 0.5, 1);
  transition-duration: 0.4s;
  transition-property: transform, background-color;
  pointer-events: none;
  margin-top: 1px;
  margin-left: 1px;
}

// Checked Knob (Green Style)
input[type='checkbox'].toggle:checked + div > div {
  transform: translate3d(20px, 0, 0);
  transform: translate3d(20px, 0, 0);
  background-color: #ffffff;
}
</style>
