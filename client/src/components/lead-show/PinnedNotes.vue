<template>
  <div class="pinned-notes">
    <div class="header">
      Pinned Notes
    </div>
    <div class="note">
      <div class="note-header">
        <span>Primary Note</span>
        <img class="expand" src="@/assets/images/dropdown-arrow.svg" alt="dropdown icon" />
      </div>
      <div class="note-content">
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
      </div>
    </div>
    <div class="note">
      <div class="note-header">
        <span>Secondary Note</span>
        <img class="expand" src="@/assets/images/dropdown-arrow.svg" alt="dropdown icon" />
      </div>
      <div class="note-content">
        Lorem Ipsum is simply dummy text of the printing and typesetting industry.
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PinnedNotes',
}
</script>

<style lang="scss" scoped>
.pinned-notes {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px #f2f2f3;
  background-color: #ffffff;
  display: flex;
  flex-flow: column;
  width: 100%;
  font-family: 'Lato', sans-serif;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: #110f24;
}

.header {
  height: 48px;
  display: flex;
  flex-flow: row;
  align-items: center;
  box-shadow: 0 1px 0 0 #ececee;
  padding-left: 3%;
  font-weight: bold;
}

.note {
  display: flex;
  flex-flow: column;
  padding: 20px 3%;
  border-bottom: solid 1px #f2f2f3;
}

.note-header {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 10px;

  .expand {
    margin-left: auto;

    &:hover {
      cursor: pointer;
    }
  }
}

.note-content {
  color: rgba($color: #110f24, $alpha: 0.4);
}
</style>
