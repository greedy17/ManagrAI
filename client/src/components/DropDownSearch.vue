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
      <template v-slot:tn-dropdown-option="{ option }">
        <slot name="tn-dropdown-option" :option="option"></slot>
      </template>
      <img src="@/assets/images/dropdown.png" alt="" />
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
  @include base-font-styles();
  border-radius: 0.25rem;
  background-color: $panther;
  border: 2px solid white;
  color: $panther-silver;
  margin-top: 1.5rem;
}

::v-deep .tn-dropdown__options__container:hover,
::v-deep .tn-dropdown__selection-container:hover {
  border: 2px solid white;
  color: $panther-silver;
}

::v-deep .tn-dropdown__options__option:hover {
  color: white;
  background-color: $panther;
}

::v-deep .tn-dropdown__selection-container {
  @include base-font-styles();
  border-radius: 0.25rem;
  border: 2px solid $white;
  box-sizing: border-box;
  line-height: 1.29;
  letter-spacing: 0.5px;
  color: $panther-silver;

  height: 2.5rem;
  background-color: white;
  box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.5);
  .tn-dropdown__search {
    @include input-field-white();
    border: none;
    background-color: white;
    &:focus {
      box-shadow: 0 0 0 0;
      background-color: white;
      color: $panther-silver;
    }
  }
}
::v-deep .tn-dropdown {
  width: 12vw;
}

::v-deep .tn-dropdown__trigger-icon {
  margin-right: 0.25rem;
  color: white;
}

::v-deep .tn-dropdown__selected-items--multi__item {
  font-size: 16px;
  background-color: white;
  color: $panther-silver;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
}

::v-deep
  .tn-dropdown__selected-items--multi.tn-dropdown__selected-items--multi--searchable.tn-dropdown__selected-items--multi--visible {
  transform: translateY(0%);
  -webkit-transform: translateY(0%);
}
::v-deep .tn-dropdown__selected-items__item-selection,
::v-deep .tn-dropdown__selected-items__item-selection--muted {
  color: $panther-silver;
}
</style>
