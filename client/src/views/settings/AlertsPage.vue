<template>
  <div>
    <ExpandablePanel
      :title="
        `${
          alertTemplateForm.field.resourceType.value
            ? alertTemplateForm.field.resourceType.value
            : 'Select Resource'
        }`
      "
    >
      <template slot="panel-content">
        <DropDownSearch
          :items.sync="SOBJECTS_LIST"
          v-model="alertTemplateForm.field.resourceType.value"
          displayKey="key"
          valueKey="value"
          nullDisplay="Salesforce Resources"
          searchable
          local
        />
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Build Alert">
      <template slot="panel-content">
        <FormField placeholder="Alert Title" large />
        <FormField placeholder="Occurences" small />
        <template v-for="(alertGroup, index) in alertTemplateForm.field.alertGroup.groups">
          <AlertGroup
            :key="index"
            :form="alertGroup"
            :resourceType="alertTemplateForm.field.resourceType.value"
          />
        </template>
        <button @click="addAlertGroup">+ Group</button>
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Construct Message">
      <template slot="panel-content">
        <div>
          Construct a message to send to your users
          <br />
          Special formatting options:
          <ul>
            <li>*bold*</li>
            <li>_italics_</li>
            <li>~strike through~</li>
          </ul>
          Dynamic Values available for any of the selected resource fields encased in {{}}
          <ul>
            <li>{{ '\{\{' + alertTemplateForm.field.resourceType.value + '.Name' + '\}\}' }}</li>
            <li>{{ '\{\{' + 'User.fullName' + '\}\}' }}</li>
          </ul>
          <FormField large placeholder="Snippet in slack notification" />
          <ElasticTextArea
            v-model="alertTemplateForm.field.alertMessage.groups[0].field.body.value"
          />
        </div>
      </template>
    </ExpandablePanel>
    <ExpandablePanel title="Preview Alert Configuration">
      <template slot="panel-content">
        {{ alertTemplateForm.value }}
      </template>
    </ExpandablePanel>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import ElasticTextArea from '@thinknimble/elastic-text-area'
import FormField from '@/components/forms/FormField'
//Internal
import AlertGroup from '@/views/settings/_pages/_AlertGroup'
import ListContainer from '@/components/ListContainer'
//import FormField from '@/components/forms/FormField'
import DropDownSearch from '@/components/DropDownSearch'
import ExpandablePanel from '@/components/ExpandablePanel'

/**
 * Services
 */

import { SOBJECTS_LIST } from '@/services/salesforce'
import { AlertGroupForm, AlertTemplateForm } from '@/services/alerts/forms'

export default {
  name: 'AlertsPage',
  components: {
    ExpandablePanel,
    DropDownSearch,
    ListContainer,
    AlertGroup,
    ElasticTextArea,
    FormField,
  },
  data() {
    return {
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: ['User.fullName'],
    }
  },
  watch: {
    selectedBindings: {
      deep: true,
      immediate: true,
      handler(val) {
        this.alertTemplateForm.field.alertMessage.groups[0].field.bindings.value = val
      },
    },
  },
  methods: {
    addAlertGroup() {
      this.alertTemplateForm.addToArray('alertGroup', new AlertGroupForm())
    },
  },
}
</script>

<style lang="scss" scoped></style>
