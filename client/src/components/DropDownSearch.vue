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
      <template v-if="$attrs.hasNext" v-slot:tn-dropdown__pagination>
        <div
          @click.stop="$emit('load-more')"
          class="tn-dropdown__options__option tn-dropdown__options__option__pagination"
        >
          +
        </div>
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
@import '@/styles/mixins/inputs.scss';
::v-deep .tn-dropdown__options__container {
  top: 50px;
  background-color: white;
  @include input-field-white();
}

::v-deep .tn-dropdown__selection-container {
  @include input-field-white();
}
::v-deep .tn-dropdown__selection-container {
  @include input-field-white();
  .tn-dropdown__search {
    @include input-field-white();
    border: none;
    &:focus {
      box-shadow: 0 0 0 0;
      outline: none;
      background-color: $white;
    }
  }
}
::v-deep .tn-dropdown {
}

::v-deep .tn-dropdown__trigger-icon {
  margin-right: 0.25rem;
}

.dropdown-search__select ::v-deep .tn-dropdown__search {
}
</style>
