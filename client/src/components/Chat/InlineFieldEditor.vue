<template>
  <div>
    <div
      class="field-container"
      v-if="dataType === 'TextArea' || dataType === 'String' || dataType.toLowerCase() === 'email'"
    >
      <textarea
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
        :disabled="inlineLoader"
        class="inline-input"
        :value="inlinePlaceholder"
        :name="apiName"
        rows="1"
      />

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span>&#x2713;</span>
        </div>
        <div @click="closeInline" class="close">
          <span>x</span>
        </div>
      </div>
    </div>

    <div
      class="field-container"
      v-else-if="
        dataType === 'Date' ||
        dataType === 'Datetime' ||
        dataType === 'Double' ||
        dataType === 'Currency'
      "
    >
      <input
        class="inline-input"
        v-if="dataType !== 'Double' || dataType !== 'Currency'"
        :value="inlinePlaceholder"
        :type="dataType"
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
        :disabled="inlineLoader"
      />
      <input
        :value="inlinePlaceholder"
        @input=";(value = $event.target.value), setUpdateValues(apiName, value)"
        :disabled="inlineLoader"
        class="inline-input"
        v-else
        type="number"
      />

      <div :class="{ disabled: inlineLoader }" class="save-close">
        <div @click="inlineUpdate" class="save">
          <span>&#x2713;</span>
        </div>
        <div @click="closeInline" class="close">
          <span>x</span>
        </div>
      </div>
    </div>

    <div
      class="field-container"
      v-else-if="dataType === 'Picklist' || dataType === 'MultiPicklist'"
    >
      picklist here
    </div>

    <div class="field-container" v-else-if="dataType === 'Reference'">{{ dataType }}</div>

    <div class="field-container" v-else>Can't update {{ dataType }} fields... yet</div>
  </div>
</template>

<script>
import { CRMObjects } from '@/services/crm'

export default {
  name: 'InlineFieldEditor',
  data() {
    return {
      formData: {},
      inlineLoader: false,
    }
  },
  props: {
    dataType: {
      type: String,
    },
    apiName: {
      type: String,
    },
    inlinePlaceholder: {
      type: String,
    },
    integrationId: {
      type: String,
    },
    resourceId: {
      type: String,
    },
    resourceType: {
      type: String,
    },
  },
  methods: {
    setUpdateValues(key, val) {
      this.formData[key] = val
    },
    closeInline() {
      this.$emit('close-inline')
    },
    async inlineUpdate() {
      this.inlineLoader = true
      try {
        const res = await CRMObjects.api.updateResource({
          form_data: this.formData,
          resource_type: this.resourceType,
          form_type: 'UPDATE',
          resource_id: this.resourceId,
          integration_ids: [this.integrationId],
          from_workflow: false,
          workflow_title: 'None',
        })
      } catch (e) {
        console.log(e)
      } finally {
        this.inlineLoader = false
        this.closeInline()
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.inline-input {
  outline: none;
  padding: 0.5rem 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  color: $base-gray;
  width: 100%;
}

::-webkit-calendar-picker-indicator {
  filter: invert(40%);
  cursor: pointer;
}

.field-container {
  position: relative;
  // background-color: white;
  padding-top: 1rem;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.save-close {
  position: absolute;
  right: 0;
  top: -1rem;
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
</style>