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
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.pinned-notes {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.05);
  border: solid 1px $soft-gray;
  background-color: $white;
  display: flex;
  flex-flow: column;
  width: 100%;
  font-family: $base-font-family, $backup-base-font-family;
  font-size: 14px;
  font-stretch: normal;
  font-style: normal;
  line-height: 1.14;
  letter-spacing: normal;
  color: $main-font-gray;
}

.header {
  height: 48px;
  display: flex;
  flex-flow: row;
  align-items: center;
  box-shadow: 0 1px 0 0 $soft-gray;
  padding-left: 3%;
  font-weight: bold;
}

.note {
  display: flex;
  flex-flow: column;
  padding: 20px 3%;
  border-bottom: solid 1px $soft-gray;
}

.note-header {
  display: flex;
  flex-flow: row;
  align-items: center;
  margin-bottom: 10px;

  .expand {
    @include pointer-on-hover();
    margin-left: auto;
  }
}

.note-content {
  color: rgba($color: $main-font-gray, $alpha: 0.4);
}
</style>
