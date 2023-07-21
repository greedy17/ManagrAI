<template>
  <div class="alert-operand-row">
    <!-- <div class="toggle__switch" v-if="form.field.operandOrder.value != 0"> -->
    <!-- <label :class="this.selectedCondition !== 'AND' ? 'inactive' : ''">AND</label> -->
    <!-- <ToggleCheckBox
        v-if="userCRM !== 'HUBSPOT'"
        @input="toggleSelectedCondition"
        :value="selectedCondition !== 'AND'"
        offColor="#41b883"
        onColor="#41b883"
      /> -->
    <!-- <label v-if="userCRM !== 'HUBSPOT'" :class="this.selectedCondition !== 'OR' ? 'inactive' : ''"
        >OR</label
      > -->
    <!-- <small @click="toggleSelectedCondition" class="andOr">
        <span :class="this.selectedCondition !== 'AND' ? 'inactive' : ''">AND</span>
        <span class="space-s">|</span>
        <span :class="this.selectedCondition !== 'OR' ? 'inactive' : ''">OR</span></small
      > -->
    <!-- </div> -->

    <div class="alert-operand-row__options">
      <div>
        <FormField :errors="form.field.operandIdentifier.errors">
          <template v-slot:input>
            <Multiselect
              placeholder="Field"
              v-model="identity"
              :options="objectFields.list"
              openDirection="below"
              style="width: 120px !important; margin-right: 0.5rem"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
              :loading="dropdownLoading"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="objectFieldNextPage">
                  Load More
                  <img src="@/assets/images/plusOne.svg" class="uninvert" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Field
                </p>
              </template>
            </Multiselect>
          </template>
        </FormField>
      </div>

      <div v-if="!(selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME')">
        <FormField :errors="form.field.operandOperator.errors">
          <template v-slot:input>
            <Multiselect
              placeholder="Operator"
              v-model="selectedOperator"
              :options="operatorOpts"
              openDirection="below"
              style="width: 120px !important; margin-right: 0.5rem"
              selectLabel="Enter"
              label="label"
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Operator
                </p>
              </template>
            </Multiselect>
          </template>
        </FormField>
      </div>

      <div class="alert-operand-row__value">
        <div
          v-if="
            (selectedFieldTypeRaw == 'Picklist' || selectedFieldTypeRaw == 'Reference') &&
            selectedFieldType == 'STRING' &&
            selectedOperator.value !== 'IS_BLANK'
          "
        >
          <FormField :errors="form.field.operandValue.errors">
            <template v-slot:input>
              <Multiselect
                placeholder="Value"
                v-model="selectedOperand"
                :options="picklistOpts"
                openDirection="below"
                style="width: 120px !important; margin-right: 0.5rem"
                selectLabel="Enter"
                label="label"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Value
                  </p>
                </template>
              </Multiselect>
            </template>
          </FormField>
        </div>

        <template v-else>
          <div v-if="selectedFieldType == 'BOOLEAN' && selectedFieldTypeRaw == 'Boolean'">
            <FormField :errors="form.field.operandValue.errors">
              <template v-slot:input>
                <Multiselect
                  placeholder="Value"
                  v-model="selectedOperand"
                  :options="valueOpts"
                  openDirection="below"
                  style="width: 120px !important; margin-right: 0.5rem"
                  selectLabel="Enter"
                  label="label"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results.</p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Value
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>

          <div v-else>
            <div
              style="
                display: flex;
                flex-direction: row;
                justify-content: space-evenly;
                align-items: center;
              "
              v-if="selectedFieldType == 'DATE' || selectedFieldType == 'DATETIME'"
            >
              <div>
                <FormField :errors="form.field.operandOperator.errors">
                  <template v-slot:input>
                    <Multiselect
                      placeholder="Operator"
                      v-model="selectedOperator"
                      :options="operatorOpts"
                      openDirection="below"
                      style="width: 120px !important; margin-right: 0.5rem"
                      selectLabel="Enter"
                      label="label"
                    >
                      <template slot="noResult">
                        <p class="multi-slot">No results.</p>
                      </template>
                      <template slot="placeholder">
                        <p class="slot-icon">
                          <img src="@/assets/images/search.svg" alt="" />
                          Operator
                        </p>
                      </template>
                    </Multiselect>
                  </template>
                </FormField>
              </div>

              <div v-if="selectedOperator.value !== 'IS_BLANK'">
                <small @click="toggleSelectedOperand" class="andOr">
                  <span :class="MyOperand !== 'Negative' ? 'inactive' : ''">In the past</span>
                  <span class="space-s">|</span>
                  <span :class="MyOperand === 'Negative' ? 'inactive' : ''">In the future</span>
                </small>

                <FormField v-if="MyOperand === 'Negative'" :errors="form.field.operandValue.errors">
                  <template v-slot:input>
                    <FormField
                      @blur="form.field.operandValue.validate()"
                      v-model="form.field.operandValue.value"
                      :inputType="getInputType(form.field._operandIdentifier.value)"
                      @input="
                        (e) => {
                          negVal(e)
                        }
                      "
                      placeholder="Number of days"
                    />
                  </template>
                </FormField>

                <FormField v-else :errors="form.field.operandValue.errors">
                  <template v-slot:input>
                    <FormField
                      @blur="form.field.operandValue.validate()"
                      v-model="form.field.operandValue.value"
                      :inputType="getInputType(form.field._operandIdentifier.value)"
                      placeholder="Number of days"
                    />
                  </template>
                </FormField>
              </div>
            </div>

            <div v-else>
              <FormField
                v-if="selectedOperator.value !== 'IS_BLANK'"
                @blur="form.field.operandValue.validate()"
                :errors="form.field.operandValue.errors"
                v-model="form.field.operandValue.value"
                :inputType="getInputType(form.field._operandIdentifier.value)"
                placeholder=""
              />
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
import FormField from '@/components/forms/FormField'
/**
 * Services
 */
import { AlertOperandForm } from '@/services/alerts/'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjects, SObjectPicklist } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import {
  ALERT_DATA_TYPE_MAP,
  INPUT_TYPE_MAP,
  INTEGER,
  STRING,
  DATE,
  DECIMAL,
  DATETIME,
} from '@/services/salesforce/models'
import { decryptData } from '../../../../encryption'

export default {
  /**
   * NB VUE usually throws an error if the child component is affecting the parent props
   * in this case we are affecting the parent props but no error is thrown because we are changing
   * the object multiple levels deep (this current implementation could be seen as incorrect)
   *
   */
  name: 'AlertOperandRow',
  components: {
    ToggleCheckBox,
    FormField,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    form: { type: AlertOperandForm },
    resourceType: { type: String },
  },
  data() {
    return {
      dropdownLoading: false,
      identity: '',
      selectedOperator: '',
      selectedOperand: '',
      objectFields: CollectionManager.create({
        ModelClass: ObjectField,
        pagination: { size: 1000 },
        filters: { forAlerts: true, filterable: true, page: 1 },
      }),
      // used by dropdown as a ref field to retrieve obj of selected opt
      selectedOperandFieldRef: null,
      // used by dd as a ref field to retrieve obj of selected opt
      selectedOperandValueRef: null,
      picklistOpts: [],
      dealStageCheck: false,
      MyOperand: 'Negative',
      intOpts: [
        { label: 'Greater or equal to', value: '>=' },
        { label: 'Greater than', value: '>' },
        { label: 'Less or equal to', value: '<=' },
        { label: 'Less than', value: '<' },
        { label: 'Equal to', value: '=' },
        { label: 'Not equal to', value: '!=' },
        { label: 'Empty', value: 'IS_BLANK' },
        // string based equality
      ],
      strOpts: [
        // string based equality
        { label: 'Contains', value: 'CONTAINS' },
        { label: 'Starts With', value: 'STARTSWITH' },
        { label: 'Ends With', value: 'ENDSWITH' },
        { label: '= (Equals)', value: '=' },
        { label: '!= (Not Equals)', value: '!=' },
        { label: 'Greater or equal to', value: '>=' },
        { label: 'Greater than', value: '>' },
        { label: 'Less or equal to', value: '<=' },
        { label: 'Less than', value: '<' },
        { label: 'Equal to', value: '=' },
        { label: 'Not equal to', value: '!=' },
        { label: 'Empty', value: 'IS_BLANK' },
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
    identity: function () {
      if (this.identity) {
        this.form.field.operandIdentifier.value = this.identity.apiName
        this.form.field._operandIdentifier.value = this.objectFields.list.filter(
          (item) => item.apiName === this.identity.apiName,
        )[0]
        this.selectedOperator = null
        this.selectedOperand = null
        this.form.field.operandValue.value = null
      } else {
        this.form.field.operandIdentifier.value = null
        this.form.field._operandIdentifier.value = null
        this.selectedOperator = null
        this.selectedOperand = null
        this.form.field.operandValue.value = null
      }
    },
    selectedOperator: function () {
      if (this.selectedOperator) {
        if (this.selectedOperator.value === 'IS_BLANK') {
          this.form.field.operandValue.value = 'null'
          this.form.field.operandValue._value = 'null'
        }
        this.form.field.operandOperator.value = this.selectedOperator.value
        this.form.field._operandOperator.value = this.selectedOperator
      } else {
        this.form.field.operandOperator.value = null
        this.form.field._operandOperator.value = ''
      }
    },
    selectedOperand: function () {
      if (this.selectedOperand) {
        this.form.field._operandValue.value = this.selectedOperand
        if (this.dealStageCheck) {
          this.form.field.operandValue.value = this.selectedOperand.id
          this.dealStageCheck = false
        } else if (this.selectedOperand.value === undefined) {
          this.form.field.operandValue.value = this.selectedOperand.id
        } else {
          this.form.field.operandValue.value = this.selectedOperand.value
        }
      } else {
        this.form.field._operandValue.value = null
        this.form.field.operandValue.value = null
      }
    },
    selectedFieldRef: {
      immediate: true,
      deep: true,
      async handler(val) {
        if (val && val.apiName === 'RecordTypeId') {
          this.getRecords()
        } else if (
          val &&
          val.apiName &&
          (val.dataType == 'Picklist' || val.dataType == 'Reference')
        ) {
          await this.listPicklists({
            picklistFor: val.apiName,
            salesforceObject: this.resourceType,
          })
        }
      },
    },
    resourceType: {
      async handler(val) {
        this.objectFields.filters = {
          ...this.objectFields.filters,
          forAlerts: true,
          filterable: true,
          crmObject: val,
        }
        this.objectFields.refresh()
      },
    },
  },
  async created() {
    this.objectFields.filters = {
      ...this.objectFields.filters,
      crmObject: this.resourceType,
    }
    await this.objectFields.refresh()
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    getInputType(type) {
      if (type && INPUT_TYPE_MAP[type.dataType]) {
        return INPUT_TYPE_MAP[type.dataType]
      }
      return 'text'
    },
    async getRecords() {
      const res = await SObjects.api.getRecords()
      this.picklistOpts = res
    },
    toggleSelectedCondition() {
      this.selectedCondition == 'AND'
        ? (this.selectedCondition = 'OR')
        : (this.selectedCondition = 'AND')
    },
    toggleSelectedOperand() {
      this.form.field.operandValue.value = ''
      this.MyOperand === 'Negative' ? (this.MyOperand = 'Positive') : (this.MyOperand = 'Negative')
    },
    async objectFieldNextPage() {
      this.dropdownLoading = true
      await this.objectFields.addNextPage()
      setTimeout(() => {
        this.dropdownLoading = false
      }, 1000)
    },
    async listPicklists(query_params = {}) {
      try {
        let res
        if (this.userCRM === 'HUBSPOT') {
          const hsPicklist = this.objectFields.list.filter(
            (item) => query_params.picklistFor === item.apiName,
          )
          this.picklistOpts = hsPicklist && hsPicklist[0] ? hsPicklist[0].options : []
          if (query_params.picklistFor === 'dealstage') {
            this.dealStageCheck = true
            let dealStage = []
            for (let i = 0; i < hsPicklist[0].optionsRef.length; i++) {
              dealStage = [...dealStage, ...hsPicklist[0].optionsRef[i]]
            }
            this.picklistOpts = dealStage
          }
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists(query_params)
          this.picklistOpts = res.length ? res[0]['values'] : []
        }
      } catch (e) {
        console.log(e)
      }
    },
    negVal(val) {
      if (val <= 0) {
        val = val
      } else {
        val = val * -1
      }
      val < 0
        ? (this.form.field.operandValue.value = -Math.abs(val).toString())
        : (this.form.field.operandValue.value = '0')
    },
  },
  computed: {
    userCRM() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.crm
    },
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
    operatorOpts() {
      switch (this.selectedFieldType) {
        case INTEGER:
          return this.intOpts
        case DECIMAL:
          return this.intOpts
        case DATE:
          return this.intOpts
        case DATETIME:
          return this.intOpts
        default:
          return this.strOpts
      }
    },
    valueOpts() {
      if (this.selectedFieldType) {
        if (this.selectedFieldType == DATE || this.selectedFieldType == DATETIME) {
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

::v-deep .input-content {
  width: 120px !important;
  border: 1px solid #e8e8e8 !important;
  border-radius: 0.3rem;
  background-color: white;
  box-shadow: none !important;
  color: $base-gray;
  font-size: 12px;
}

::v-deep .input-form {
  width: 120px !important;
}
::v-deep .input-form__active {
  border: none;
}
.andOr {
  border: 1px solid $soft-gray;
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  color: $base-gray;
}
.inactive {
  color: $very-light-gray;
  font-size: 11px;
  border-radius: 4px;
}
.space-s {
  margin: 0 4px;
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
img {
  filter: invert(90%);
}
.uninvert {
  filter: invert(10%);
}
.toggle__switch {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  font-size: 11px;
  letter-spacing: 0.75px;
  color: $base-gray;

  label {
    padding: 0rem 0.2rem;
  }
}
.alert-operand-row {
  display: flex;
  flex-direction: column;
}
.alert-operand-row__options {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
}
</style>