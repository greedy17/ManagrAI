<template>
  <div class="tooltip">
    <slot name="tooltip-target"> Hover</slot>
    <span class="tooltiptext">
      <slot name="tooltip-content"> I'm Hovered</slot>
    </span>
  </div>
</template>

<script>
export default {}
</script>

<style lang="scss">
/* Tooltip container */
.tooltip {
  position: relative;
  display: inline-block;
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: #484a6e;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;

  /* Position the tooltip text - see examples below! */
  position: fixed;
  z-index: 100;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}
</style>
