<template>
  <div v-if="form.field.operandOrder.value === 0" class="alert-operand-row">
    <div class="alert-operand-row__options">
      <div
        v-if="selectedFieldType != 'DATE'"
        class="alert-operand-row__field"
        style="margin: 0 0.3rem"
      >
        <FormField :errors="form.field.operandIdentifier.errors">
          <template v-slot:input>
          </template>
        </FormField>
      </div>
      <div
        v-if="!(selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME')"
        class="alert-operand-row__operator"
        style="margin: 0 0.3rem"
      >
        <FormField :errors="form.field.operandOperator.errors">
          <template v-slot:input>
          </template>
        </FormField>
      </div>
      <div class="alert-operand-row__value">
        <FormField
          v-if="selectedFieldTypeRaw == 'Picklist' && selectedFieldType == 'STRING'"
          :errors="form.field.operandValue.errors"
        >
          <template v-slot:input>
          </template>
        </FormField>
        <template v-else>
          <FormField
            v-if="selectedFieldType == 'BOOLEAN' && selectedFieldTypeRaw == 'Boolean'"
            :errors="form.field.operandValue.errors"
          >
            <template v-slot:input>
            </template>
          </FormField>
          <div v-else>
            <FormField
              @blur="form.field.operandValue.validate()"
              :errors="form.field.operandValue.errors"
              v-model="form.field.operandValue.value"
              :inputType="getInputType(form.field._operandIdentifier.value)"
              large
              bordered
              placeholder="Enter a value"
              v-if="!(selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME')"
            />
            <div
              v-if="selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME'"
              class="column"
            >
              <span class="row"
                ><input
                  @click="setOperandDateValue(5)"
                  type="radio"
                  id="Approaching"
                  value="5"
                  v-model="operandDate"
                />
                <label for="Approaching"
                  >{{ form.field.operandIdentifier.value }} is approaching.</label
                >
              </span>
              <span class="row"
                ><input
                  @click="setOperandDateValue(-1)"
                  type="radio"
                  id="passed"
                  value="-1"
                  v-model="operandDate"
                />
                <label for="passed">{{ form.field.operandIdentifier.value }} has passed.</label>
              </span>
            </div>
          </div>
        </template>
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
/**
 * Services
 */
import { AlertOperandForm } from '@/services/alerts/'
import { CollectionManager } from '@thinknimble/tn-models'
import {
  SObjectField,
  SObjectPicklist,
  NON_FIELD_ALERT_OPTS,
} from '@/services/salesforce'
import {
  ALERT_DATA_TYPE_MAP,
  INPUT_TYPE_MAP,
  STRING
} from '@/services/salesforce/models'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'ForecastOperandRow',
  components: { ListContainer, ToggleCheckBox, FormField },
  props: {
    form: { type: AlertOperandForm },
    resourceType: { type: String },
  },
  data() {
    return {
      objectFields: CollectionManager.create({
        ModelClass: SObjectField,
        filters: { forAlerts: true, filterable: true, page: 1 },
      }),
      // used by dropdown as a ref field to retrieve obj of selected opt
      selectedOperandFieldRef: null,
      // used by dd as a ref field to retrieve obj of selected opt
      selectedOperandValueRef: null,
      picklistOpts: [],
      operandDate: '',
      NON_FIELD_ALERT_OPTS,

      intOpts: [
        { label: '>= (Greater or Equal)', value: '>=' },
        { label: '<= (Less or Equal)', value: '<=' },
        { label: '< (Less)', value: '<' },
        { label: '> (Greater)', value: '>' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
        // string based equality
      ],
      strOpts: [
        // string based equality
        { label: 'Contains', value: 'CONTAINS' },
        { label: 'Starts With', value: 'STARTSWITH' },
        { label: 'Ends With', value: 'ENDSWITH' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
      ],
      dateValueOpts: [
        { label: 'Same Day as alert day', value: '0' },
        { label: '7 days FROM alert day', value: '7' },
        { label: '7 days PRIOR TO alert day', value: '-7' },
        { label: '15 Days FROM alert day', value: '15' },
        { label: '15 Days PRIOR TO alert day', value: '-15' },
        { label: 'Month  FROM alert day', value: '30' },
        { label: 'Month  PRIOR TO alert day', value: '-30' },
      ],
      booleanValueOpts: [
        { label: 'True', value: 'true' },
        { label: 'False', value: 'false' },
      ],
    }
  },
  watch: {
    selectedFieldRef: {
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
          filterable: true,
          salesforceObject: val,
        }
        this.objectFields.refresh()
      },
    },
  },
  async created() {
    this.objectFields.filters = {
      ...this.objectFields.filters,
      salesforceObject: this.resourceType,
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
    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.picklistOpts = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    setOperandDateValue(val) {
      this.form.field.operandValue.value = val
      this.form.field.operandOperator.value = '<='
    },
  },
  computed: {
    selectedFieldTypeRaw() {
      if (this.form.field._operandIdentifier.value) {
        return this.form.field._operandIdentifier.value.dataType
      }
      return null
    },
    selectedFieldRef() {
      if (this.selectedFieldTypeRaw) {
        return this.form.field._operandIdentifier.value
      }
      return null
    },
    selectedFieldType() {
      if (this.selectedFieldTypeRaw) {
        return ALERT_DATA_TYPE_MAP[this.form.field._operandIdentifier.value.dataType]
      } else {
        return STRING
      }
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
  beforeMount() {
    if (this.form.field.operandOrder.value === 0) {
      this.form.field._operandIdentifier.value = {
        apiName: 'ForecastCategoryName',
        createable: true,
        custom: false,
        dataType: 'Picklist',
        displayValue: '',
        filterable: 'true',
        id: '1fb41560-bebd-4700-a2e6-3a161b796582',
        includeInRecap: null,
        label: 'Forecast Category',
        length: 255,
        order: null,
        reference: 'false',
        referenceDisplayLabel: 'Forecast Category',
        referenceToInfos: Array[0],
        required: false,
        unique: false,
        updateable: true,
        value: '',
      }
      this.form.field.operandIdentifier.value = 'ForecastCategoryName'
      this.form.field.operandOperator.value = '!='
      this.form.field._operandOperator.value = { label: '!= (Does Not Equal)', value: '!=' }
      this.form.field.operandValue.value = 'Commit'
    } else if (this.form.field.operandOrder.value === 1) {
      this.form.field._operandIdentifier.value = {
        apiName: 'CloseDate',
        createable: true,
        custom: false,
        dataType: 'Date',
        displayValue: '',
        filterable: 'true',
        id: '310405d5-0b5e-4c60-8493-54b26b2c3d39',
        includeInRecap: null,
        label: 'Close Date',
        length: 0,
        order: null,
        reference: 'false',
        referenceDisplayLabel: 'Close Date',
        referenceToInfos: Array[0],
        required: true,
        unique: false,
        updateable: true,
        value: '',
      }
      this.form.field.operandIdentifier.value = 'CloseDate'
      this.form.field.operandOperator.value = '<='
      this.form.field._operandOperator.value = { label: '<= (Less or Equal)', value: '<=' }
      this.form.field.operandValue.value = 14
    }
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
  display: flex;
  flex-direction: column;
}
.alert-operand-row__options {
  display: flex;
  padding: 1rem;
  flex-wrap: wrap;
  justify-content: space-evenly;
}
.column {
  display: flex;
  flex-direction: column;
  margin: 1rem;
}
.row {
  display: flex;
  flex-direction: row;
  margin: 0.2rem;
}
</style>
