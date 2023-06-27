<template>
  <div>
    <div
      class="field-container"
      :class="{ seperator: field.label === 'Notes' }"
      v-if="
        field.dataType === 'TextArea' ||
        field.dataType === 'String' ||
        field.dataType.toLowerCase() === 'email'
      "
    >
      <label for="">{{ field.label }}</label>
      <textarea
        @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
        :disabled="loader"
        class="inline-input"
        :value="placeholder"
        :name="field.apiName"
        v-autoresize
        :rows="field.label === 'Notes' ? 3 : 1"
      />
    </div>

    <div
      class="field-container"
      v-else-if="
        field.dataType === 'Date' ||
        field.dataType === 'Datetime' ||
        field.dataType === 'Double' ||
        field.dataType === 'Currency' ||
        field.dataType === 'Int'
      "
    >
      <label for="">{{ field.label }}</label>
      <input
        class="inline-input"
        v-if="field.dataType !== 'Double' || field.dataType !== 'Currency' || dataType !== 'Int'"
        :value="placeholder"
        :type="field.dataType"
        @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
        :disabled="loader"
      />
      <input
        :value="placeholder"
        @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
        :disabled="loader"
        class="inline-input"
        v-else
        type="number"
      />
    </div>

    <div
      class="field-container"
      v-else-if="
        (field.dataType === 'Picklist' || field.dataType === 'MultiPicklist') &&
        field.apiName !== 'StageName' &&
        field.apiName !== 'dealstage'
      "
    >
      <label for="">{{ field.label }}</label>
      <Multiselect
        :options="picklistOptions[field.id] || field.options"
        selectLabel=""
        track-by="value"
        label="label"
        :multiple="field.dataType === 'MultiPicklist' ? true : false"
        :placeholder="placeholder || 'select option'"
        :disabled="loader"
        selectedLabel=""
        deselectLabel=""
        v-model="stageOption[field.apiName]"
        @select="
          setUpdateValues(
            field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
            $event.value,
            field.dataType === 'MultiPicklist' ? true : false,
          )
        "
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>
    </div>

    <div
      class="field-container"
      v-else-if="field.apiName === 'StageName' || field.apiName === 'dealstage'"
    >
      <label for=""> {{ field.label }}</label>

      <Multiselect
        :options="
          picklistOptions[field.id] || field.options[0][currentOpp.secondary_data.pipeline]
            ? field.options[0][currentOpp.secondary_data.pipeline].stages
            : []
        "
        selectLabel=""
        track-by="value"
        label="label"
        :multiple="field.dataType === 'MultiPicklist' ? true : false"
        :placeholder="placeholder || 'select option'"
        :disabled="loader"
        selectedLabel=""
        deselectLabel=""
        v-model="newStage"
        @select="
          setUpdateValues(
            field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
            field.apiName === 'dealstage' ? $event.id : $event.value,
            field.dataType === 'MultiPicklist' ? true : false,
          )
        "
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>
    </div>

    <div class="field-container" v-else-if="field.dataType === 'Boolean'">
      <label for="">{{ field.label }}</label>
      <Multiselect
        :options="booleans"
        selectLabel=""
        :placeholder="placeholder || 'select option'"
        :disabled="loader"
        selectedLabel=""
        deselectLabel=""
        v-model="stageOption[field.apiName]"
        @select="
          setUpdateValues(
            field.apiName,
            $event.value,
            field.dataType === 'MultiPicklist' ? true : false,
          )
        "
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>
    </div>

    <div class="field-container" v-else-if="field.dataType === 'Reference'">
      <label for="">{{ field.label }}</label>
      <!-- :placeholder="loadingOptions ? 'Gathering options...' : placeholder || '-'" -->
      <Multiselect
        :options="referenceOpts"
        selectLabel=""
        track-by="id"
        label="name"
        :placeholder="placeholder || 'select option'"
        :disabled="loader || loadingOptions"
        :loading="loadingOptions"
        v-model="stageOption[field.apiName]"
        @select="setUpdateValues(field.apiName, $event.id, false)"
        @open="getReferenceOptions(field.id)"
        selectedLabel=""
        deselectLabel=""
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>
    </div>

    <div class="field-container" v-else>Can't update {{ field.dataType }} fields... yet</div>
    <div ref="StageFormEnd" class="stage-container" v-if="showStageForm">
      <p class="stage-title row">
        <img src="@/assets/images/warning.svg" class="filter-blue" height="16px" alt="" />
        This stage has required fields
      </p>
      <div v-for="(field, i) in stageFields[selectedStage]" :key="i">
        <div
          class="field-container"
          v-if="
            field.dataType === 'TextArea' ||
            field.dataType === 'String' ||
            field.dataType.toLowerCase() === 'email'
          "
        >
          <label for="">{{ field.label }}</label>
          <textarea
            @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
            :disabled="loader"
            class="inline-input"
            :name="field.apiName"
            v-autoresize
            rows="1"
          />
        </div>

        <div
          class="field-container"
          v-else-if="
            field.dataType === 'Date' ||
            field.dataType === 'Datetime' ||
            field.dataType === 'Double' ||
            field.dataType === 'Currency'
          "
        >
          <label for="">{{ field.label }}</label>
          <input
            class="inline-input"
            v-if="field.dataType !== 'Double' || field.dataType !== 'Currency'"
            :type="field.dataType"
            @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
            :disabled="loader"
          />
          <input
            @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
            :disabled="loader"
            class="inline-input"
            v-else
            type="number"
          />
        </div>

        <div
          class="field-container"
          v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'"
        >
          <label for="">{{ field.label }}</label>
          <Multiselect
            :options="picklistOptions[field.id]"
            selectLabel=""
            track-by="value"
            label="label"
            :multiple="field.dataType === 'MultiPicklist' ? true : false"
            :disabled="loader"
            selectedLabel=""
            deselectLabel=""
            v-model="stageOption[field.apiName]"
            @select="
              setUpdateValues(
                field.apiName === 'ForecastCategory' ? 'ForecastCategoryName' : field.apiName,
                $event.value,
                field.dataType === 'MultiPicklist' ? true : false,
              )
            "
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div class="field-container" v-else-if="field.dataType === 'Boolean'">
          <label for="">{{ field.label }}</label>
          <Multiselect
            :options="booleans"
            selectLabel=""
            :disabled="loader"
            selectedLabel=""
            deselectLabel=""
            v-model="stageOption[field.apiName]"
            @select="
              setUpdateValues(
                field.apiName,
                $event.value,
                field.dataType === 'MultiPicklist' ? true : false,
              )
            "
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>

        <div class="field-container" v-else-if="field.dataType === 'Reference'">
          <label for="">{{ field.label }}</label>
          <!-- :placeholder="loadingOptions ? 'Gathering options...' : placeholder || '-'" -->
          <Multiselect
            :options="referenceOpts"
            selectLabel=""
            track-by="id"
            label="name"
            :disabled="loader || loadingOptions"
            :loading="loadingOptions"
            v-model="stageOption[field.apiName]"
            @select="setUpdateValues(field.apiName, $event.id, false)"
            @open="getReferenceOptions(field.id)"
            selectedLabel=""
            deselectLabel=""
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>
          </Multiselect>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { SObjects } from '@/services/salesforce'

export default {
  name: 'ChatFormField',
  data() {
    return {
      formData: {},
      loader: false,
      showStageForm: false,
      selectedOption: null,
      booleans: ['true', 'false'],
      loadingOptions: false,
      referenceOpts: [],
      selectedStage: null,
      stageOption: {},
      newStage: null,
    }
  },
  watch: {
    newStage(val) {
      if (this.stagesWithForms.includes(val.value)) {
        this.showStageForm = true
        this.selectedStage = val.value
        setTimeout(() => {
          this.$refs.StageFormEnd
            ? this.$refs.StageFormEnd.scrollIntoView({ behavior: 'smooth' })
            : null
        }, 300)
      } else {
        this.showStageForm = false
      }
    },
  },
  components: {
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    placeholder: {
      type: String,
    },
    field: {},
    chatData: {},
    stageFields: {},
    stagesWithForms: {},
  },
  methods: {
    test(op) {
      console.log(op)
    },
    setUpdateValues(key, val, multi) {
      this.$emit('set-value', key, val, multi)
    },
    closeInline() {
      this.$emit('close-inline')
    },
    scrollToStages() {
      this.$refs.StageFormEnd
        ? this.$refs.StageFormEnd.scrollIntoView({ behavior: 'smooth' })
        : null

      console.log('efevndefvujkn')
    },
    async getReferenceOptions(id) {
      this.loadingOptions = true
      try {
        let res = await SObjects.api.getSobjectPicklistValues({
          sobject_id: id,
          value: '',
          for_filter: null,
        })

        this.referenceOpts = res

        console.log(res)
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.loadingOptions = false
        })
      }
    },
  },
  computed: {
    picklistOptions() {
      return this.$store.state.allPicklistOptions
    },
    currentOpp() {
      return this.$store.state.currentOpp
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

::v-deep .multiselect * {
  font-size: 13px;
  font-family: $base-font-family;
  border-radius: 5px !important;
}
::v-deep .multiselect__option--highlight {
  background-color: $off-white;
  color: $base-gray;
}
::v-deep .multiselect__option--selected {
  background-color: $soft-gray;
}

::v-deep .multiselect__content-wrapper {
  border-radius: 5px;
  margin: 0.5rem 0rem;
  border-top: 1px solid $soft-gray;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
::v-deep .multiselect__placeholder {
  color: $base-gray;
}

.stage-container {
  // border-left: 1px solid $light-gray-blue;
  margin-top: 1.5rem;

  border-radius: 4px;
  position: relative;

  label {
    color: $coral;
  }
}

.seperator {
  border-bottom: 1px solid $soft-gray;
  border-radius: 0 !important;
  padding-bottom: 1.25rem;
}

.filter-blue {
  filter: invert(73%) sepia(4%) saturate(1902%) hue-rotate(200deg) brightness(83%) contrast(84%);
  margin-right: 0.25rem;
}

.stage-title {
  color: $light-gray-blue;
  font-size: 13px;
  margin-bottom: 0;
  position: absolute;
  top: -1.5rem;

  background-color: white;
  padding: 0 2px;
}

label {
  font-size: 12px;
  font-family: $base-font-family;
  margin-bottom: 8px;
}

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
  width: 100%;
  font-family: $base-font-family;
  font-size: 12px;
  line-height: 1.5;
  letter-spacing: 0.4px;
  resize: none;
}

::-webkit-calendar-picker-indicator {
  filter: invert(40%);
  cursor: pointer;
}

.field-container {
  position: relative;
  padding-top: 1rem;
  border-radius: 4px;
}

.save-close {
  position: absolute;
  right: 0;
  top: -1.5rem;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.close {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $coral;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  margin-left: 0.5rem;
  margin-right: 2px;
  font-size: 13px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }
}

.save {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  outline: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-green;
  width: 20px;
  height: 20px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 3px 6px 0 $very-light-gray;
    scale: 1.025;
  }
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  // background-color: $soft-gray;
  border-radius: 6px;
  padding: 0.75rem 0.75rem;
}

.dot {
  width: 6px;
  height: 6px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

button {
  @include chat-button();
  padding: 0.5rem;
  margin-top: 0.5rem;
  background-color: $dark-green;
  color: white;
  border: none;
  font-size: 12px;
}

.flex-end {
  display: flex;

  align-items: center;
}

.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotate {
  animation: rotation 1s infinite linear;
}

.row {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>