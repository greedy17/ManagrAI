<template>
  <div class="alert-operand-row">
    <span class="alert-operand-row--label">Alert Operands</span>
    <div class="alert-operand-row__condition" v-if="form.field.operandOrder.value != 0">
      <label class="alert-operand-row__condition-label">AND</label>
      <ToggleCheckBox
        @input="toggleSelectedCondition"
        :value="selectedCondition !== 'AND'"
        offColor="#199e54"
        onColor="#199e54"
      />
      <label class="alert-operand-row__condition-label">OR</label>
    </div>
    <div class="alert-operand-row__options">
      <div class="alert-operand-row__field">
        <div class="alert-operand-row__condition">
          <label class="alert-operand-row__condition-label">Field Level Alert</label>
          <ToggleCheckBox
            @input="
              selectedOperandType == 'FIELD'
                ? (selectedOperandType = 'NON_FIELD')
                : (selectedOperandType = 'FIELD')
            "
            :value="selectedOperandType !== 'FIELD'"
            offColor="#199e54"
            onColor="#199e54"
          />
          <label class="alert-operand-row__condition-label">Non Field Level Alert</label>
        </div>
        <DropDownSearch
          v-if="selectedOperandType == 'FIELD'"
          :items="objectFields.list"
          :itemsRef.sync="form.field._operandIdentifier.value"
          v-model="form.field.operandIdentifier.value"
          displayKey="referenceDisplayLabel"
          valueKey="apiName"
          nullDisplay="Select a field"
          searchable
          :hasNext="!!objectFields.pagination.hasNextPage"
          @load-more="objectFieldNextPage"
          @search-term="onSearchFields"
        />
        <DropDownSearch
          v-else-if="selectedOperandType == 'NON_FIELD'"
          :items.sync="NON_FIELD_ALERT_OPTS[resourceType]"
          :itemsRef.sync="form.field._operandIdentifier.value"
          v-model="form.field.operandIdentifier.value"
          displayKey="referenceDisplayLabel"
          valueKey="apiName"
          :nullDisplay="
            NON_FIELD_ALERT_OPTS[resourceType].length ? 'Select an option' : 'Not Options Available'
          "
          :disabled="!NON_FIELD_ALERT_OPTS[resourceType].length"
          searchable
          local
        />
      </div>
      <div class="alert-operand-row__operator">
        <DropDownSearch
          :items.sync="operatorOpts"
          :itemsRef.sync="form.field._operandOperator.value"
          v-model="form.field.operandOperator.value"
          displayKey="label"
          valueKey="value"
          nullDisplay="Select an Operator"
          searchable
          local
        />
      </div>
      <div class="alert-operand-row__value">
        <DropDownSearch
          v-if="selectedFieldType && selectedFieldType.dataType == 'Picklist'"
          :items.sync="picklistOpts"
          :itemsRef.sync="form.field._operandValue.value"
          v-model="form.field.operandValue.value"
          displayKey="label"
          valueKey="value"
          nullDisplay="Select a value"
          searchable
          local
        />
        <DropDownSearch
          v-else-if="
            selectedFieldType &&
              (selectedFieldType.dataType == 'Date' ||
                selectedFieldType.dataType == 'DateTime' ||
                selectedFieldType.dataType == 'Boolean')
          "
          :items.sync="valueOpts"
          :itemsRef.sync="form.field._operandValue.value"
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
          :inputType="getInputType(form.field._operandIdentifier.value)"
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
import {
  SObjectField,
  SObjectValidations,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
} from '@/services/salesforce'
import {
  ALERT_DATA_TYPE_MAP,
  INPUT_TYPE_MAP,
  INTEGER,
  STRING,
  DATE,
  DECIMAL,
} from '@/services/salesforce/models'

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
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        filters: { forAlerts: true },
      }),

      // used by dropdown as a ref field to retrieve obj of selected opt
      selectedOperandFieldRef: null,
      // used by dd as a ref field to retrieve obj of selected opt
      selectedOperandValueRef: null,
      picklistOpts: [],
      NON_FIELD_ALERT_OPTS,

      operatorOpts: [
        { label: '>= (Greater or Equal)', value: 'gte' },
        { label: '<= (Less or Equal)', value: 'lte' },
        { label: '< (Less)', value: 'lt' },
        { label: '> (Greater)', value: 'gt' },
        { label: '= (Equal)', value: 'eq' },
      ],
      dateValueOpts: [
        { label: 'Same Day', value: '0' },
        { label: '15 Days', value: '15' },
        { label: 'One Month', value: '30' },
      ],
      booleanValueOpts: [
        { label: 'True', value: 'true' },
        { label: 'False', value: 'false' },
      ],
    }
  },
  watch: {
    selectedFieldType: {
      immediate: true,
      deep: true,
      async handler(val) {
        if (val && val.apiName && val.dataType == 'Picklist') {
          await this.listPicklists({ picklistFor: val.apiName })
        }
      },
    },
    resourceType: {
      async handler(val) {
        this.objectFields.filters = {
          ...this.objectFields.filters,
          forAlerts: true,
          salesforceObject: val,
        }
        this.objectFields.refresh()
      },
    },
  },
  async created() {
    this.objectFields.filters = {
      ...this.objectFields.filters,
      salesforceObject: val,
    }
    await this.objectFields.refresh()
  },
  methods: {
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
    },
    toggleSelectedCondition() {
      this.selectedCondition == 'AND'
        ? (this.selectedCondition = 'OR')
        : (this.selectedCondition = 'AND')
    },
    async objectFieldNextPage() {
      await this.objectFields.addNextPage()
    },
    async onSearchFields(v) {
      this.objectFields.pagination = new Pagination()
      this.objectFields.filters = {
        ...this.objectFields.filters,
        search: v,
      }
      await this.objectFields.refresh()
    },
    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.picklistOpts = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
  },
  computed: {
    selectedField() {
      return this.form.field.operandIdentifier.value
    },
    selectedFieldType() {
      return this.form.field._operandIdentifier.value
    },
    valueOpts() {
      if (this.selectedFieldType) {
        if (
          this.selectedFieldType.dataType == 'Date' ||
          this.selectedFieldType.dataType == 'DateTime'
        ) {
          return this.dateValueOpts
        } else {
          return this.booleanValueOpts
        }
      }
      return this.booleanValueOpts
    },
    selectedCondition: {
      get() {
        return this.form.field.operandCondition.value
      },
      set(val) {
        this.form.field.operandCondition.value = val
      },
    },
    selectedOperandType: {
      get() {
        return this.form.field.operandType.value
      },
      set(val) {
        this.form.field.operandType.value = val
      },
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
.btn {
  &--primary {
    @include primary-button();
  }
}

.alert-operand-row {
  @include standard-border();
  margin: 1rem;
  padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  overflow: visible;
  &--label {
    top: -1.05rem;
    position: relative;
    @include muted-font();
  }
}
.alert-operand-row__condition {
  position: relative;
  top: -2rem;
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
