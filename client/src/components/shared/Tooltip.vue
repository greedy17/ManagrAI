<template>
  <div class="tn-tooltip">
    <slot name="tn-tooltip-target"> Hover</slot>
    <span class="tn-tooltiptext">
      <slot name="tn-tooltip-content"> I'm Hovered</slot>
    </span>
  </div>
</template>

<script>
export default {}
</script>

<style lang="scss">
/* tn-tooltip container */
.tn-tooltip {
  position: relative;
  display: inline-block;
}

/* tn-tooltip text */
.tn-tooltip .tn-tooltiptext {
  visibility: hidden;
  width: 120px;
  background-color: #484a6e;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;

  /* Position the tn-tooltip text - see examples below! */
  position: fixed;
  z-index: 100;
}

/* Show the tn-tooltip text when you mouse over the tn-tooltip container */
.tn-tooltip:hover .tn-tooltiptext {
  visibility: visible;
}
</style>
