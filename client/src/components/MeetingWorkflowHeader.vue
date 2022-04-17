<template>
  <div class="table-row">
    <!-- <div style="padding: 2vh" class="table-cell-checkbox-header">
      <div>
        <input type="checkbox" id="checkAll" />
        <label for="checkAll"></label>
      </div>
    </div> -->

    <div class="cell-name-header">Meeting Title</div>
    <div class="table-cell-header" v-for="(column, i) in columns" :key="i">
      {{ column }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'MeetingWorkflowHeader',
  data() {
    return {
      columns: ['# of Attendees', 'Attendees', 'Account/Opportunity', 'Actions'],
    }
  },
  components: {},
  computed: {},
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::v-deep .multiselect {
  min-width: 7rem;
}
.red {
  filter: invert(46%) sepia(37%) saturate(832%) hue-rotate(308deg) brightness(104%) contrast(104%);
  height: 0.75rem;
}
.add-field-section {
  z-index: 5;
  position: absolute;
  right: 0.5rem;
  top: 9vh;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 22vw;
  overflow: visible;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-weight: bold;
    font-size: 16px;
    width: 100%;
  }
  &__body {
    min-height: 3rem;
    padding-left: 1rem;
    margin-top: 1rem;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 1rem;
    width: 100%;
    min-height: 6vh;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      color: $dark-green;
      font-weight: bold;
    }
  }
}
.remove-field-section {
  z-index: 5;
  position: absolute;
  right: 0;
  top: 9vh;
  border-radius: 0.33rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $white;
  min-width: 16rem;
  box-shadow: 1px 1px 7px 2px $very-light-gray;
  &__title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: $base-gray;
    background-color: $off-white;
    letter-spacing: 0.4px;
    padding-left: 1rem;
    font-weight: bold;
    font-size: 14px;
    width: 100%;
    height: 3rem;
  }
  &__body {
    height: 3rem;
    margin-left: 5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
  }
  &__footer {
    display: flex;
    align-items: center;
    justify-content: space-evenly;
    width: 100%;
    height: 3rem;
    border-top: 1px solid $soft-gray;
    p {
      cursor: pointer;
      // color: $dark-green;
      font-weight: bold;
    }
  }
}

.sort-img-visible {
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;
}
.sort-img-visible > img {
  display: none;
}
.sort-img-visible:hover > img {
  display: block;
}
.table-row {
  display: table-row;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 3;
  width: 4vw;
  top: 0;
  left: 0;
  position: sticky;
  background-color: $off-white;
}
.cell-name-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 3;
  left: 0;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 13px;
  letter-spacing: 0.5px;
  color: $base-gray;
}
.add-row {
  height: 1rem;
  margin-left: 0.25rem;
  padding-right: 0.25rem;
  filter: invert(36%) sepia(81%) saturate(5047%) hue-rotate(139deg) brightness(77%) contrast(80%);
}
.direction-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  cursor: pointer;
  color: $dark-green;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;

  img {
    margin-left: 0.5rem;
  }
}
</style>