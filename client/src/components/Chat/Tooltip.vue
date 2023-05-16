<template>
  <div class="tooltip">
    <img :src="source" height="14px" alt="" />
    <span class="tooltiptext">
      {{ text }}
    </span>
  </div>
</template>

<script>
export default {
  name: 'Tooltip',
  props: {
    text: {
      type: String,
      default: '',
    },
    source: {
      type: String,
      default: '',
    },
  },
}
</script>

<style lang="scss" scoped>
.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;

  /* Position the tooltip text - see examples below! */
  position: absolute;
  z-index: 1;
  top: 100%;
  left: 50%;
  margin-left: -60px; /* Use half of the width to center the tooltip */
}

.tooltip:hover .tooltiptext {
  visibility: visible;
}

.tooltip .tooltiptext::after {
  content: ' ';
  position: absolute;
  bottom: 100%; /* At the top of the tooltip */
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: transparent transparent black transparent;
}
</style>