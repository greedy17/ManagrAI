<template>
  <div class="status-dropdown" @click.stop>
    <select
      :value="leadItem.status"
      :style="{ 'background-color': getStatusColor }"
      :disabled="disabled || getIsClosed"
      @change="onChange"
    >
      <option :value="null">---</option>
      <option v-for="option in getStatuses" :key="option.id" :value="option.id">
        {{ option.title.toLowerCase() }}
      </option>
    </select>
    <Modal
      v-if="modal.isOpen"
      dimmed
      @close-modal="closeModal"
      @closed-lead="$emit('closed-lead')"
      :width="50"
    >
      <CloseLead @closed-lead="updateLeadItem" :lead="leadItem" />
    </Modal>
  </div>
</template>

<script>
import { statusEnums } from '@/services/leads/enumerables'
import Lead from '@/services/leads'
import { getLightenedColor } from '@/services/getColorFromLeadStatus'
import CloseLead from '@/components/shared/CloseLead'

export default {
  name: 'LeadStatusDropdown',
  components: { CloseLead },
  props: {
    lead: {
      required: true,
      type: Object,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      selectedOptionColor: null,
      statusEnums,
      modal: {
        isOpen: false,
      },
      options: [],
      leadItem: this.lead,
    }
  },
  created() {
    this.leadItem = this.lead
  },
  methods: {
    updateLeadItem(val) {
      let closedStatus = this.getStatuses.find(i => i.title == Lead.CLOSED)
      this.leadItem = { ...val, statusRef: closedStatus, status: closedStatus.id }

      this.closeModal()
      this.$emit('closed-lead', this.leadItem)
    },
    async onChange({ target: { value } }) {
      let val = this.getStatuses.find(s => s.id == value)
      if (!value || val.title != 'CLOSED') {
        try {
          this.loading = true
          await this.updateStatus(value)
          this.$emit('status-changed', val)
        } finally {
          this.loading = false
        }
      } else {
        // All custom-fields must be completed in order to close a lead
        if (this.leadCanBeClosed) {
          this.modal.isOpen = true
        } else {
          let prevVal = this.leadItem.status
          this.leadItem.status = null
          this.leadItem.status = prevVal
          this.$Alert.alert({
            type: 'error',
            timeout: 3000,
            message: 'All custom-fields must be completed to close a lead.',
          })
        }
      }
    },
    updateStatus(status) {
      Lead.api.update(this.lead.id, { status }).then(lead => {
        this.lead.statusRef = lead.statusRef
        this.leadItem = lead
      })
    },
    closeModal() {
      this.modal.isOpen = false
    },
  },
  computed: {
    getStatusColor() {
      return this.leadItem.statusRef
        ? getLightenedColor(this.leadItem.statusRef.color, 0.9)
        : getLightenedColor('#9B9B9B')
    },
    getStatuses() {
      return this.$store.state.stages
    },
    getValue() {
      return this.leadItem.statusRef ? this.leadItem.statusRef.title : null
    },
    getIsClosed() {
      return this.leadItem.statusRef ? this.leadItem.statusRef.title == 'CLOSED' : false
    },
    leadCanBeClosed() {
      // All custom-fields must be completed in order to close a lead
      let fields = ['companySize', 'industry', 'competitor', 'geographyAddress', 'type', 'custom']
      for (let f of fields) {
        if (!this.lead[f]) {
          return false
        }
      }
      return true
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/utils';

.status-dropdown {
  width: 6.25rem;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0); // rgb irrelevant, this is for the alpha / transparency

  select {
    @include pointer-on-hover();
    @include base-font-styles();
    width: 96%;
    height: 100%;
    padding: 0.125rem 1rem;
    line-height: 1.6;
    color: $white;
    font-size: 10px;
    font-weight: bold;
    border: unset;
    text-transform: capitalize;

    &:focus {
      outline: none;
    }
  }
}
</style>
