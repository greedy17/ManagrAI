<template>
  <div class="alert-operand-row">
    <span class="alert-operand-row--label">Alert Operands</span>
    <div class="alert-operand-row__condition">
      <label class="alert-operand-row__condition-label">AND</label>
      <ToggleCheckBox
        @input="
          selectedCondition == 'AND' ? (selectedCondition = 'OR') : (selectedCondition = 'AND')
        "
        :value="selectedCondition == 'AND'"
        offColor="#199e54"
        onColor="#199e54"
      />
      <label class="alert-operand-row__condition-label">OR</label>
    </div>
    <div class="alert-operand-row__options">
      <div class="alert-operand-row__field">
        <DropDownSearch
          :items="objectFields.list"
          v-model="form.field.operandField.value"
          displayKey="referenceDisplayLabel"
          valueKey="apiName"
          nullDisplay="Select a field"
          searchable
          :hasNext="!!objectFields.pagination.hasNextPage"
          @load-more="objectFieldNextPage"
          @search-term="onSearchFields"
        />
      </div>
      <div class="alert-operand-row__operator">
        <DropDownSearch
          :items.sync="operatorOpts"
          v-model="form.field.operandOperator.value"
          displayKey="label"
          valueKey="value"
          nullDisplay="Select an Operator"
          searchable
          local
          small
        />
      </div>
      <div class="alert-operand-row__value">
        <DropDownSearch
          v-if="false"
          :items.sync="operatorOpts"
          :itemsRef.sync="form.field.operandValue.value"
          v-model="form.field.operandValue.value"
          displayKey="label"
          valueKey="value"
          nullDisplay="Select a value"
          searchable
          local
        />
        <FormField
          v-else
          @blur="form.field.operandValue.validate()"
          :itemsRef.sync="form.field.operandValue.value"
          :errors="form.field.operandValue.errors"
          v-model="form.field.operandValue.value"
          large
          bordered
          placeholder="Enter a value"
        />
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import ToggleCheckBox from '@thinknimble/togglecheckbox'
//Internal
import ListContainer from '@/components/ListContainer'
import FormField from '@/components/forms/FormField'
import DropDownSearch from '@/components/DropDownSearch'
/**
 * Services
 */
import { AlertOperandForm } from '@/services/alerts/'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import { SObjectField, SObjectValidations, SObjectPicklist } from '@/services/salesforce'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertOperandRow',
  components: { ListContainer, ToggleCheckBox, DropDownSearch, FormField },
  props: {
    form: { type: AlertOperandForm },
    resourceType: { type: String },
  },
  data() {
    return {
      objectFields: CollectionManager.create({ ModelClass: SObjectField }),
      selectedCondition: 'AND',

      operatorOpts: [
        { label: '>= (Greater or Equal)', value: 'gte' },
        { label: '<= (Less or Equal)', value: 'lte' },
        { label: '< (Less)', value: 'lt' },
        { label: '> (Greater)', value: 'gt' },
        { lable: '= (Equal)', value: 'eq' },
      ],
    }
  },
  watch: {
    selectedCondition: {
      immediate: true,
      handler(val) {
        this.form.field.operandCondition.value = val
      },
    },
    resourceType: {
      async handler(val) {
        this.objectFields.filters.salesforceObject = val
        this.objectFields.refresh()
      },
    },
  },
  async created() {
    this.objectFields.filters.salesforceObject = this.resourceType
    this.objectFields.refresh()
  },
  methods: {
    async objectFieldNextPage() {
      await this.objectFields.nextPage()
    },
    async onSearchFields(v) {
      this.objectFields.pagination = new Pagination()
      this.objectFields.filters = {
        ...this.objectFields.filters,
        search: v,
      }
      await this.objectFields.refresh()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';

.alert-operand-row {
  @include standard-border();
  margin: 1rem;
  padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  overflow: none;
  &--label {
    top: -1.05rem;
    position: relative;
    @include muted-font();
  }
}
.alert-operand-row__condition {
  position: relative;
  top: -2.4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  &-label {
    @include muted-font();
    margin: 0 0.5rem;
  }
}
.alert-operand-row__options {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  &-label {
    color: black;
  }
}
</style>
