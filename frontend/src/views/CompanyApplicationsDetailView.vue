<template>
  <AppLayout>
    <PageHeader
      eyebrow="Company workspace"
      title="Application details"
      back-to="/company/applications"
      back-label="Applications"
    />

    <SkeletonBlock v-if="loading" height="220px" border-radius="16px" />
    <StateMessage
      v-else-if="!application"
      icon="fas fa-file-alt"
      title="Application not found"
      description="This application may have been removed or you are not authorized to view it."
    />

    <template v-else>
      <DetailHero
        :name="application.student.name"
        :email="application.student.email"
        id-label="Status"
        :id-value="application.status || 'N/A'"
        avatar-icon="fas fa-user"
      >
        <template #badge>
          <StatusBadge :status="application.status" />
        </template>
      </DetailHero>

      <InfoSection
        title="Application"
        icon="fas fa-file"
        :items="[
          { label: 'Drive', value: application.drive.job_title },
          { label: 'Applied', value: formatDate(application.application_date) },
          {
            label: 'Joining Date',
            value:
              application.status === 'selected' && application.join_date
                ? formatDate(application.join_date)
                : 'Not set',
          },
        ]"
      />

      <div class="pp-panel mb-4">
        <h3 class="pp-section-title">
          <i class="fas fa-align-left" aria-hidden="true"></i>Cover letter
        </h3>
        <div class="pp-panel p-3 bg-light" style="white-space: pre-wrap">
          {{ application.cover_letter || "No cover letter provided." }}
        </div>
      </div>

      <div class="pp-panel mb-4">
        <h3 class="pp-section-title">
          <i class="fas fa-user" aria-hidden="true"></i>Resume
        </h3>
        <a
          v-if="application.resume_link"
          :href="application.resume_link"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-pp-outline btn-sm"
          >View resume</a
        >
        <div v-else class="text-muted">No resume available.</div>
      </div>

      <div class="pp-panel">
        <h3 class="pp-section-title">
          <i class="fas fa-gears" aria-hidden="true"></i>Actions
        </h3>
        <div class="d-flex gap-4 flex-wrap">
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="applied"
              value="Applied"
              v-model="status"
              name="app-status"
            />
            <label class="form-check-label" for="applied">Applied</label>
          </div>

          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="shortlisted"
              value="Shortlisted"
              v-model="status"
              name="app-status"
            />
            <label class="form-check-label" for="shortlisted">Shortlisted</label>
          </div>

          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="selected"
              value="Selected"
              v-model="status"
              name="app-status"
            />
            <label class="form-check-label" for="selected">Selected</label>
          </div>

          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="rejected"
              value="Rejected"
              v-model="status"
              name="app-status"
            />
            <label class="form-check-label" for="rejected">Rejected</label>
          </div>
        </div>
        <div>
          <label class="pp-form-label small mb-1">Remarks</label>
          <input v-model="remark" class="form-control" placeholder="Remarks" />
        </div>
        <div class="d-flex justify-content-end">
          <button class="btn-pp-primary btn-sm" @click="save">Save</button>
        </div>
      </div>
    </template>
    <div
      v-if="showJoiningDateModal"
      class="modal d-block"
      tabindex="-1"
      style="background: rgba(0, 0, 0, 0.35)"
    >
      <div class="modal-dialog modal-sm modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Select Joining Date</h5>
          </div>

          <div class="modal-body">
            <input
              type="date"
              v-model="joiningDate"
              class="form-control"
              :min="minDate"
            />
          </div>

          <div class="modal-footer">
            <button class="btn-pp-outline btn-sm" @click="cancelJoiningDate">
              Cancel
            </button>

            <button class="btn-pp-primary btn-sm" @click="confirmJoiningDate">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import PageHeader from "../components/PageHeader.vue";
import DetailHero from "../components/DetailHero.vue";
import InfoSection from "../components/InfoSection.vue";
import StateMessage from "../components/StateMessage.vue";
import SkeletonBlock from "../components/SkeletonBlock.vue";
import StatusBadge from "../components/StatusBadge.vue";
import http from "../api/http";
import { useToast } from "../composables/useToast";

const route = useRoute();
const toast = useToast();
const loading = ref(true);
const application = ref(null);
const status = ref("Applied");
const remark = ref("");
const joiningDate = ref("");
const showJoiningDateModal = ref(false);
const minDate = new Date().toISOString().slice(0, 10);

onMounted(loadApplication);

const STATUS_LABELS = {
  applied: "Applied",
  shortlisted: "Shortlisted",
  selected: "Selected",
  rejected: "Rejected",
};

async function loadApplication() {
  loading.value = true;
  try {
    const resp = await http.get(`/api/v1/company/applications/${route.params.id}`);
    application.value = resp.data.application;

    if (application.value) {
      status.value = STATUS_LABELS[application.value.status] || "Applied"; 
      remark.value = application.value.remarks || "";
      joiningDate.value = application.value.join_date
        ? application.value.join_date.slice(0, 10)
        : "";
    }
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function save() {

  if (status.value === "Selected" && !joiningDate.value) {
    toast.error("Please select a joining date.");
    showJoiningDateModal.value = true;
    return;
  }

  try {
    await http.post(`/api/v1/company/applications/${route.params.id}/status`, {
      status: status.value,
      remark: remark.value,
      join_date: status.value === "Selected" ? joiningDate.value : null,
    });

    toast.success("Application updated successfully.");

    
    showJoiningDateModal.value = false;

    
    await loadApplication();
  } catch (err) {
    toast.error(err.response?.data?.message || "Unable to update application.");
  }
}

function confirmJoiningDate() {
  if (!joiningDate.value) {
    toast.error("Please select a joining date.");
    return;
  }

  showJoiningDateModal.value = false;
  save();
}

function cancelJoiningDate() {
  status.value = application.value.status;
  joiningDate.value = "";
  showJoiningDateModal.value = false;
}

function formatDate(value) {
  return value
    ? new Date(value).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      })
    : "N/A";
}
</script>

<style scoped>
.pp-panel .btn-pp-outline {
  margin-right: 8px;
}
</style>
