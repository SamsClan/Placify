<template>
  <AppLayout>
    <PageHeader
      eyebrow="Company workspace"
      title="Shortlisted candidate"
      back-to="/company/shortlisted"
      back-label="Shortlisted"
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

      <div class="pp-panel">
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
    </template>
  </AppLayout>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import AppLayout from "../layouts/AppLayout.vue";
import PageHeader from "../components/PageHeader.vue";
import DetailHero from "../components/DetailHero.vue";
import InfoSection from "../components/InfoSection.vue";
import StateMessage from "../components/StateMessage.vue";
import SkeletonBlock from "../components/SkeletonBlock.vue";
import StatusBadge from "../components/StatusBadge.vue";
import http from "../api/http.js";

const route = useRoute();
const loading = ref(true);
const application = ref(null);

onMounted(loadApplication);

async function loadApplication() {
  loading.value = true;
  try {
    const resp = await http.get(`/api/v1/company/applications/${route.params.id}`);
    application.value = resp.data.application || null;
  } catch (err) {
    console.error(err);
    application.value = null;
  } finally {
    loading.value = false;
  }
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
