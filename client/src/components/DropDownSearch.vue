<template>
  <div class="dropdown-search">
    <DropDownSelect v-bind="$attrs" v-on="$listeners" class="dropdown-search__select">
      <template v-slot:tn-dropdown-trigger-icon>
        <span
          class="tn-dropdown__trigger-icon"
          :class="{ 'tn-dropdown__trigger-icon--expanded-local': visible }"
        >
        </span>
      </template>
    </DropDownSelect>
  </div>
</template>

<script>
import DropDownSelect from '@thinknimble/dropdownselect'

export default {
  name: 'DropDownSearch',
  components: { DropDownSelect },
  computed: {
    // this is not the right way to do this (the component needs to be updated to pass back the event)
    // TODO: PB 11/02/2020 this is just a temp fix
    visible() {
      return this.$children[0].visible
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';
::v-deep .tn-dropdown__options__container {
  top: 50px;
  background-color: white;
}

.dropdown ::v-deep .tn-dropdown__selection-container {
  background-color: white;
  border: 1px solid grey;
  width: 12rem;
  height: 2.4rem;
}
::v-deep .tn-dropdown {
}

::v-deep .tn-dropdown__trigger-icon {
  margin-right: 0.25rem;
}

.dropdown-search__select ::v-deep .tn-dropdown__search {
}
</style>
