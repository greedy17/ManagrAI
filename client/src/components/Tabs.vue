<template>
  <div class="wrapper">
    <div class="tabs">
      <div class="tab">
        <input type="radio" name="css-tabs" id="tab-1" checked class="tab-switch" />
        <label for="tab-1" class="tab-label">History</label>
        <div class="tab-content">
          <div>
            <small>01/02/34</small>
            <p>Stage</p>
            <s>Booked</s>
            <p>Best Case</p>
          </div>
          <div>
            <small>01/22/34</small>
            <p>Stage</p>
            <s>Best Case</s>
            <p>Discovery</p>
          </div>
          <!-- <div>
            <small>01/28/34</small>
            <p>Stage</p>
            <p>Booked</p>
          </div> -->
        </div>
      </div>
      <!-- <div class="tab">
        <input type="radio" name="css-tabs" id="tab-2" class="tab-switch" />
        <label for="tab-2" class="tab-label">Factors</label>
        <div class="tab-content">
          <div>
            <p>Factor 1</p>
          </div>
          <div>
            <p>Factor 2</p>
          </div>
          <div>
            <p>Factor 3</p>
          </div>
        </div>
      </div> -->
      <div class="tab">
        <input type="radio" name="css-tabs" id="tab-3" class="tab-switch" />
        <label for="tab-3" class="tab-label">Notes</label>
        <div class="tab-content">
          <section>
            <h4>Note Title</h4>
            <p>
              lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum lorem ipsum
              lorem ipsum lorem ipsum lorem ipsum lorem ipsum
            </p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Tabs',
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

* {
  box-sizing: border-box;
}
body {
  font-family: 'Open Sans';
  background: #2c3e50;
  color: #ecf0f1;
  line-height: 1.618em;
}
.wrapper {
  width: 100%;
  margin: 0 auto;
  font-size: 14px;
  letter-spacing: 0.75px;
}
.tabs {
  position: relative;
  margin: 3rem 0;
  background: white;
  //   height: 14.75rem;
}
.tabs::before,
.tabs::after {
  content: '';
  display: table;
}
.tabs::after {
  clear: both;
}
.tab {
  float: left;
}
.tab-switch {
  display: none;
}
.tab-label {
  position: relative;
  display: block;
  line-height: 2.75em;
  height: 3em;
  padding: 0 1.618em;
  color: $light-gray-blue;
  cursor: pointer;
  top: 0;
  transition: all 0.25s;
}
.tab-label:hover {
  top: -0.25rem;
  transition: top 0.25s;
}
.tab-content {
  height: 12rem;
  position: absolute;
  z-index: 1;
  top: 2.75em;
  left: 0;
  padding: 1.618rem;
  background: #fff;
  color: $base-gray;
  opacity: 0;
  transition: all 0.35s;
  overflow: scroll;

  div {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: flex-start;
    width: 25vw;
    overflow-x: scroll;
    small {
      margin-right: 32px;
    }
    p {
      margin-right: 32px;
    }
    s {
      margin-right: 32px;
    }
  }
}
.tab-switch:checked + .tab-label {
  background: #fff;
  color: #2c3e50;
  border-bottom: 0;
  //   border-right: 1px solid $soft-gray;
  //   border-left: 1px solid $soft-gray;
  //   border-top: 1px solid $soft-gray;
  //   border-top-left-radius: 6px;
  //   border-top-right-radius: 6px;
  transition: all 0.35s;
  z-index: 1;
  top: -0.0625rem;
}
.tab-switch:checked + label + .tab-content {
  z-index: 2;
  opacity: 1;
  transition: all 0.35s;
}
</style>